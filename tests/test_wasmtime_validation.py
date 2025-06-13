import pytest
import wasmtime

from wasmai import Module, encode_binary, encode_text
from wasmai.instructions import (
    AtomicMemoryInstruction,
    AtomicOpcode,
    ConstInstruction,
    Instruction,
    LocalInstruction,
    Opcode,
)
from wasmai.sections import (
    CodeSection,
    Export,
    ExportSection,
    Func,
    FuncExportDesc,
    FunctionSection,
    TypeSection,
)
from wasmai.types import FuncType, ValType


def test_simple_add_function_validation():
    """Test that a simple add function can be validated by wasmtime."""
    # Create a simple WASM module with an add function
    module = Module()

    # Type section
    func_type = FuncType(params=[ValType.I32, ValType.I32], results=[ValType.I32])
    type_section = TypeSection(types=[func_type])
    module.add_section(type_section)

    # Function section
    function_section = FunctionSection(type_indices=[0])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(exports=[Export(name='add', desc=FuncExportDesc(func_idx=0))])
    module.add_section(export_section)

    # Code section
    add_func = Func(
        locals=[],
        body=[
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=1),
            Instruction(opcode=Opcode.I32_ADD),
            Instruction(opcode=Opcode.RETURN),
        ],
    )
    code_section = CodeSection(funcs=[add_func])
    module.add_section(code_section)

    # Encode to binary and validate with wasmtime
    binary_data = encode_binary(module)

    # This should not raise an exception if the module is valid
    engine = wasmtime.Engine()
    wasmtime_module = wasmtime.Module(engine, binary_data)

    # Verify the module has the expected export
    store = wasmtime.Store(engine)
    instance = wasmtime.Instance(store, wasmtime_module, [])
    add_func = instance.exports(store)['add']

    # Test the function works
    result = add_func(store, 5, 3)
    assert result == 8


def test_text_format_generation():
    """Test that we can generate valid WAT text format."""
    # Create a simple WASM module
    module = Module()

    # Type section
    func_type = FuncType(params=[ValType.I32], results=[ValType.I32])
    type_section = TypeSection(types=[func_type])
    module.add_section(type_section)

    # Function section
    function_section = FunctionSection(type_indices=[0])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(exports=[Export(name='square', desc=FuncExportDesc(func_idx=0))])
    module.add_section(export_section)

    # Code section - square function: x * x
    square_func = Func(
        locals=[],
        body=[
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),
            Instruction(opcode=Opcode.I32_MUL),
            Instruction(opcode=Opcode.RETURN),
        ],
    )
    code_section = CodeSection(funcs=[square_func])
    module.add_section(code_section)

    # Generate text format
    wat_text = encode_text(module)

    # Verify the text contains expected components
    assert '(module' in wat_text
    assert '(func' in wat_text
    assert '(export "square"' in wat_text
    assert 'local.get' in wat_text
    assert 'i32.mul' in wat_text

    # The text should be valid enough that it contains proper structure
    assert wat_text.count('(') == wat_text.count(')')


def test_memory_operations_validation():
    """Test a module with memory operations."""
    module = Module()

    # Type section
    func_type = FuncType(params=[ValType.I32, ValType.I32], results=[ValType.I32])
    type_section = TypeSection(types=[func_type])
    module.add_section(type_section)

    # Import memory (since we can't easily create a valid memory section)
    from wasmai.sections import (
        Import,
        ImportSection,
        MemImportDesc,
    )
    from wasmai.types import Limits, MemType

    memory_import = Import(
        module='env',
        name='memory',
        desc=MemImportDesc(mem_type=MemType(limits=Limits(min=1))),
    )
    import_section = ImportSection(imports=[memory_import])
    module.add_section(import_section)

    # Function section
    function_section = FunctionSection(type_indices=[0])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(
        exports=[Export(name='load_i32', desc=FuncExportDesc(func_idx=0))]
    )
    module.add_section(export_section)

    # Code section - load i32 from memory
    from wasmai.instructions import MemoryInstruction

    load_func = Func(
        locals=[],
        body=[
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),  # address
            MemoryInstruction(opcode=Opcode.I32_LOAD, align=2, offset=0),
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=1),  # value
            Instruction(opcode=Opcode.I32_ADD),
            Instruction(opcode=Opcode.RETURN),
        ],
    )
    code_section = CodeSection(funcs=[load_func])
    module.add_section(code_section)

    # Encode to binary
    binary_data = encode_binary(module)

    # Create memory for the import
    engine = wasmtime.Engine()
    limits = wasmtime.Limits(1, None)
    memory = wasmtime.Memory(wasmtime.Store(engine), wasmtime.MemoryType(limits))

    # Validate with wasmtime
    wasmtime_module = wasmtime.Module(engine, binary_data)

    # This validates that the module structure is correct
    assert wasmtime_module is not None


def test_multiple_functions_validation():
    """Test a module with multiple functions."""
    module = Module()

    # Type section - multiple function types
    add_type = FuncType(params=[ValType.I32, ValType.I32], results=[ValType.I32])
    sub_type = FuncType(params=[ValType.I32, ValType.I32], results=[ValType.I32])
    type_section = TypeSection(types=[add_type, sub_type])
    module.add_section(type_section)

    # Function section - two functions
    function_section = FunctionSection(type_indices=[0, 1])
    module.add_section(function_section)

    # Export section - export both functions
    export_section = ExportSection(
        exports=[
            Export(name='add', desc=FuncExportDesc(func_idx=0)),
            Export(name='sub', desc=FuncExportDesc(func_idx=1)),
        ]
    )
    module.add_section(export_section)

    # Code section
    add_func = Func(
        locals=[],
        body=[
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=1),
            Instruction(opcode=Opcode.I32_ADD),
            Instruction(opcode=Opcode.RETURN),
        ],
    )

    sub_func = Func(
        locals=[],
        body=[
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=1),
            Instruction(opcode=Opcode.I32_SUB),
            Instruction(opcode=Opcode.RETURN),
        ],
    )

    code_section = CodeSection(funcs=[add_func, sub_func])
    module.add_section(code_section)

    # Encode and validate
    binary_data = encode_binary(module)
    engine = wasmtime.Engine()
    wasmtime_module = wasmtime.Module(engine, binary_data)

    # Test both functions
    store = wasmtime.Store(engine)
    instance = wasmtime.Instance(store, wasmtime_module, [])
    exports = instance.exports(store)

    add_func = exports['add']
    sub_func = exports['sub']

    assert add_func(store, 10, 5) == 15
    assert sub_func(store, 10, 5) == 5


def test_constants_validation():
    """Test a module with various constant operations."""
    module = Module()

    # Type section
    func_type = FuncType(params=[], results=[ValType.F32])
    type_section = TypeSection(types=[func_type])
    module.add_section(type_section)

    # Function section
    function_section = FunctionSection(type_indices=[0])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(exports=[Export(name='get_pi', desc=FuncExportDesc(func_idx=0))])
    module.add_section(export_section)

    # Code section - return pi as f32
    pi_func = Func(
        locals=[],
        body=[
            ConstInstruction(opcode=Opcode.F32_CONST, value=3.14159),
            Instruction(opcode=Opcode.RETURN),
        ],
    )
    code_section = CodeSection(funcs=[pi_func])
    module.add_section(code_section)

    # Encode and validate
    binary_data = encode_binary(module)
    engine = wasmtime.Engine()
    wasmtime_module = wasmtime.Module(engine, binary_data)

    # Test the function
    store = wasmtime.Store(engine)
    instance = wasmtime.Instance(store, wasmtime_module, [])
    get_pi_func = instance.exports(store)['get_pi']

    result = get_pi_func(store)
    assert abs(result - 3.14159) < 0.00001
