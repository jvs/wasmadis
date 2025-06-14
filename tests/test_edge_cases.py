import pytest
import wasmtime

from wasmadis import Module, encode_binary, encode_text
from wasmadis.instructions import ConstInstruction, Instruction, Opcode
from wasmadis.sections import (
    CodeSection,
    Export,
    ExportSection,
    Func,
    FuncExportDesc,
    FunctionSection,
    TypeSection,
)
from wasmadis.types import FuncType, ValType


def test_empty_module():
    """Test that an empty module can be encoded and is valid."""
    module = Module()

    # An empty module should still be valid WASM
    binary_data = encode_binary(module)

    # Should contain at least the magic number and version
    assert len(binary_data) >= 8
    assert binary_data[:4] == b'\x00asm'

    # Should be valid according to wasmtime
    engine = wasmtime.Engine()
    wasmtime_module = wasmtime.Module(engine, binary_data)
    assert wasmtime_module is not None


def test_module_with_only_types():
    """Test a module that only has a type section."""
    module = Module()

    # Just type definitions, no functions
    func_type1 = FuncType(params=[ValType.I32], results=[ValType.I32])
    func_type2 = FuncType(params=[ValType.F32, ValType.F32], results=[ValType.F32])
    type_section = TypeSection(types=[func_type1, func_type2])
    module.add_section(type_section)

    binary_data = encode_binary(module)
    engine = wasmtime.Engine()
    wasmtime_module = wasmtime.Module(engine, binary_data)
    assert wasmtime_module is not None


def test_function_with_no_instructions():
    """Test a function with an empty body (should be invalid but test structure)."""
    module = Module()

    # Type section
    func_type = FuncType(params=[], results=[])
    type_section = TypeSection(types=[func_type])
    module.add_section(type_section)

    # Function section
    function_section = FunctionSection(type_indices=[0])
    module.add_section(function_section)

    # Code section with empty function body
    empty_func = Func(locals=[], body=[])
    code_section = CodeSection(funcs=[empty_func])
    module.add_section(code_section)

    # This should encode without error
    binary_data = encode_binary(module)
    assert len(binary_data) > 8  # More than just header


def test_function_with_unreachable():
    """Test a function that starts with unreachable instruction."""
    module = Module()

    # Type section
    func_type = FuncType(params=[], results=[ValType.I32])
    type_section = TypeSection(types=[func_type])
    module.add_section(type_section)

    # Function section
    function_section = FunctionSection(type_indices=[0])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(
        exports=[Export(name='unreachable_func', desc=FuncExportDesc(func_idx=0))]
    )
    module.add_section(export_section)

    # Code section with unreachable
    unreachable_func = Func(
        locals=[],
        body=[
            Instruction(opcode=Opcode.UNREACHABLE),
            ConstInstruction(opcode=Opcode.I32_CONST, value=42),  # Dead code
            Instruction(opcode=Opcode.RETURN),
        ],
    )
    code_section = CodeSection(funcs=[unreachable_func])
    module.add_section(code_section)

    # Encode and validate structure
    binary_data = encode_binary(module)
    engine = wasmtime.Engine()
    wasmtime_module = wasmtime.Module(engine, binary_data)

    # The function should exist but trap when called
    store = wasmtime.Store(engine)
    instance = wasmtime.Instance(store, wasmtime_module, [])
    unreachable_func = instance.exports(store)['unreachable_func']

    # Calling this should raise a trap
    with pytest.raises(wasmtime.Trap):
        unreachable_func(store)


def test_large_constants():
    """Test functions with large constant values."""
    module = Module()

    # Type section
    func_type = FuncType(params=[], results=[ValType.I64])
    type_section = TypeSection(types=[func_type])
    module.add_section(type_section)

    # Function section
    function_section = FunctionSection(type_indices=[0])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(
        exports=[Export(name='large_const', desc=FuncExportDesc(func_idx=0))]
    )
    module.add_section(export_section)

    # Code section with large constant
    large_const_func = Func(
        locals=[],
        body=[
            ConstInstruction(opcode=Opcode.I64_CONST, value=9223372036854775807),  # Max i64
            Instruction(opcode=Opcode.RETURN),
        ],
    )
    code_section = CodeSection(funcs=[large_const_func])
    module.add_section(code_section)

    # Encode and test
    binary_data = encode_binary(module)
    engine = wasmtime.Engine()
    wasmtime_module = wasmtime.Module(engine, binary_data)

    store = wasmtime.Store(engine)
    instance = wasmtime.Instance(store, wasmtime_module, [])
    large_const_func = instance.exports(store)['large_const']

    result = large_const_func(store)
    assert result == 9223372036854775807


def test_negative_constants():
    """Test functions with negative constant values."""
    module = Module()

    # Type section
    func_type = FuncType(params=[], results=[ValType.I32])
    type_section = TypeSection(types=[func_type])
    module.add_section(type_section)

    # Function section
    function_section = FunctionSection(type_indices=[0])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(
        exports=[Export(name='negative_const', desc=FuncExportDesc(func_idx=0))]
    )
    module.add_section(export_section)

    # Code section with negative constant
    negative_const_func = Func(
        locals=[],
        body=[
            ConstInstruction(opcode=Opcode.I32_CONST, value=-42),
            Instruction(opcode=Opcode.RETURN),
        ],
    )
    code_section = CodeSection(funcs=[negative_const_func])
    module.add_section(code_section)

    # Encode and test
    binary_data = encode_binary(module)
    engine = wasmtime.Engine()
    wasmtime_module = wasmtime.Module(engine, binary_data)

    store = wasmtime.Store(engine)
    instance = wasmtime.Instance(store, wasmtime_module, [])
    negative_const_func = instance.exports(store)['negative_const']

    result = negative_const_func(store)
    assert result == -42


def test_text_format_edge_cases():
    """Test text format generation with edge cases."""
    module = Module()

    # Type section with multiple types
    func_type1 = FuncType(params=[], results=[])
    func_type2 = FuncType(
        params=[ValType.I32, ValType.I32, ValType.I32], results=[ValType.I32, ValType.I32]
    )
    type_section = TypeSection(types=[func_type1, func_type2])
    module.add_section(type_section)

    # Generate text
    wat_text = encode_text(module)

    # Check structure
    assert '(module' in wat_text
    assert '(type' in wat_text
    assert wat_text.count('(') == wat_text.count(')')

    # Should contain type definitions
    assert 'func' in wat_text
    assert 'param i32' in wat_text
    assert 'result i32' in wat_text


def test_module_version():
    """Test that module version is correctly encoded."""
    module = Module(version=1)

    binary_data = encode_binary(module)

    # Check magic number and version
    assert binary_data[:4] == b'\x00asm'
    # Version should be 1 (little endian)
    assert binary_data[4:8] == b'\x01\x00\x00\x00'


def test_very_simple_working_function():
    """Test the simplest possible working function."""
    module = Module()

    # Type section - no params, returns i32
    func_type = FuncType(params=[], results=[ValType.I32])
    type_section = TypeSection(types=[func_type])
    module.add_section(type_section)

    # Function section
    function_section = FunctionSection(type_indices=[0])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(exports=[Export(name='get_42', desc=FuncExportDesc(func_idx=0))])
    module.add_section(export_section)

    # Code section - simplest possible: return constant
    simple_func = Func(
        locals=[],
        body=[
            ConstInstruction(opcode=Opcode.I32_CONST, value=42),
            Instruction(opcode=Opcode.RETURN),
        ],
    )
    code_section = CodeSection(funcs=[simple_func])
    module.add_section(code_section)

    # Encode and test
    binary_data = encode_binary(module)
    engine = wasmtime.Engine()
    wasmtime_module = wasmtime.Module(engine, binary_data)

    store = wasmtime.Store(engine)
    instance = wasmtime.Instance(store, wasmtime_module, [])
    get_42_func = instance.exports(store)['get_42']

    result = get_42_func(store)
    assert result == 42
