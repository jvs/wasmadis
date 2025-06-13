import pytest
import wasmtime

from wasmai import Module, encode_binary
from wasmai.instructions import (
    ConstInstruction,
    Instruction,
    LocalInstruction,
    MemoryInstruction,
    Opcode,
    CallInstruction,
    IfInstruction,
    BlockInstruction,
    BrInstruction,
    GlobalInstruction,
)
from wasmai.sections import (
    CodeSection,
    Export,
    ExportSection,
    Func,
    FuncExportDesc,
    FunctionSection,
    GlobalExportDesc,
    GlobalSection,
    Import,
    ImportSection,
    MemExportDesc,
    MemImportDesc,
    TypeSection,
    Global,
    Locals,
)
from wasmai.types import FuncType, ValType, GlobalType, MemType, Limits


def test_simple_counter_execution():
    """Test a simple counter with increment and decrement operations."""
    module = Module()

    # Type section
    inc_type = FuncType(params=[ValType.I32], results=[ValType.I32])  # increment by n
    dec_type = FuncType(params=[ValType.I32], results=[ValType.I32])  # decrement by n

    type_section = TypeSection(types=[inc_type, dec_type])
    module.add_section(type_section)

    # Function section
    function_section = FunctionSection(type_indices=[0, 1])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(
        exports=[
            Export(name='increment', desc=FuncExportDesc(func_idx=0)),
            Export(name='decrement', desc=FuncExportDesc(func_idx=1)),
        ]
    )
    module.add_section(export_section)

    # Code section
    increment_func = Func(
        locals=[],
        body=[
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),  # get input
            ConstInstruction(opcode=Opcode.I32_CONST, value=1),
            Instruction(opcode=Opcode.I32_ADD),  # add 1
            Instruction(opcode=Opcode.RETURN),
        ],
    )

    decrement_func = Func(
        locals=[],
        body=[
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),  # get input
            ConstInstruction(opcode=Opcode.I32_CONST, value=1),
            Instruction(opcode=Opcode.I32_SUB),  # subtract 1
            Instruction(opcode=Opcode.RETURN),
        ],
    )

    code_section = CodeSection(funcs=[increment_func, decrement_func])
    module.add_section(code_section)

    # Execute and test
    binary_data = encode_binary(module)
    engine = wasmtime.Engine()
    wasmtime_module = wasmtime.Module(engine, binary_data)
    store = wasmtime.Store(engine)
    instance = wasmtime.Instance(store, wasmtime_module, [])

    increment = instance.exports(store)['increment']
    decrement = instance.exports(store)['decrement']

    # Test basic operations
    assert increment(store, 5) == 6
    assert increment(store, 0) == 1
    assert increment(store, -1) == 0

    assert decrement(store, 5) == 4
    assert decrement(store, 1) == 0
    assert decrement(store, 0) == -1

    # Test chaining operations conceptually
    result = 10
    result = increment(store, result)  # 11
    result = increment(store, result)  # 12
    result = decrement(store, result)  # 11
    assert result == 11


def test_memory_operations_with_side_effects():
    """Test memory operations by writing and reading values, verifying side effects."""
    module = Module()

    # Type section - functions for memory operations
    write_type = FuncType(params=[ValType.I32, ValType.I32], results=[])  # write(addr, value)
    read_type = FuncType(params=[ValType.I32], results=[ValType.I32])  # read(addr) -> value
    sum_type = FuncType(params=[ValType.I32], results=[ValType.I32])  # sum_array(length) -> sum

    type_section = TypeSection(types=[write_type, read_type, sum_type])
    module.add_section(type_section)

    # Import memory
    memory_import = Import(
        module='env',
        name='memory',
        desc=MemImportDesc(mem_type=MemType(limits=Limits(min=1))),
    )
    import_section = ImportSection(imports=[memory_import])
    module.add_section(import_section)

    # Function section
    function_section = FunctionSection(type_indices=[0, 1, 2])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(
        exports=[
            Export(name='write', desc=FuncExportDesc(func_idx=0)),
            Export(name='read', desc=FuncExportDesc(func_idx=1)),
            Export(name='sum_array', desc=FuncExportDesc(func_idx=2)),
        ]
    )
    module.add_section(export_section)

    # Code section
    write_func = Func(
        locals=[],
        body=[
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),  # addr
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=1),  # value
            MemoryInstruction(opcode=Opcode.I32_STORE, align=2, offset=0),
            Instruction(opcode=Opcode.RETURN),
        ],
    )

    read_func = Func(
        locals=[],
        body=[
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),  # addr
            MemoryInstruction(opcode=Opcode.I32_LOAD, align=2, offset=0),
            Instruction(opcode=Opcode.RETURN),
        ],
    )

    # Sum array function - demonstrates loop with memory access
    sum_func = Func(
        locals=[
            Locals(count=2, val_type=ValType.I32),  # sum, i
        ],
        body=[
            ConstInstruction(opcode=Opcode.I32_CONST, value=0),  # sum = 0
            LocalInstruction(opcode=Opcode.LOCAL_SET, local_idx=1),
            ConstInstruction(opcode=Opcode.I32_CONST, value=0),  # i = 0
            LocalInstruction(opcode=Opcode.LOCAL_SET, local_idx=2),
            # Simple sum of first 3 values at addresses 0, 4, 8
            ConstInstruction(opcode=Opcode.I32_CONST, value=0),
            MemoryInstruction(opcode=Opcode.I32_LOAD, align=2, offset=0),
            LocalInstruction(opcode=Opcode.LOCAL_SET, local_idx=1),  # sum = mem[0]
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=1),  # sum
            ConstInstruction(opcode=Opcode.I32_CONST, value=4),
            MemoryInstruction(opcode=Opcode.I32_LOAD, align=2, offset=0),
            Instruction(opcode=Opcode.I32_ADD),
            LocalInstruction(opcode=Opcode.LOCAL_SET, local_idx=1),  # sum += mem[4]
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=1),  # sum
            ConstInstruction(opcode=Opcode.I32_CONST, value=8),
            MemoryInstruction(opcode=Opcode.I32_LOAD, align=2, offset=0),
            Instruction(opcode=Opcode.I32_ADD),
            LocalInstruction(opcode=Opcode.LOCAL_SET, local_idx=1),  # sum += mem[8]
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=1),  # return sum
            Instruction(opcode=Opcode.RETURN),
        ],
    )

    code_section = CodeSection(funcs=[write_func, read_func, sum_func])
    module.add_section(code_section)

    # Execute and test side effects
    binary_data = encode_binary(module)
    engine = wasmtime.Engine()
    wasmtime_module = wasmtime.Module(engine, binary_data)
    store = wasmtime.Store(engine)

    # Create memory for import
    memory = wasmtime.Memory(store, wasmtime.MemoryType(wasmtime.Limits(1, None)))
    instance = wasmtime.Instance(store, wasmtime_module, [memory])

    write_func = instance.exports(store)['write']
    read_func = instance.exports(store)['read']
    sum_func = instance.exports(store)['sum_array']

    # Test 1: Write and read single values
    write_func(store, 0, 42)
    assert read_func(store, 0) == 42

    write_func(store, 4, 100)
    assert read_func(store, 4) == 100

    # Verify first value is still there
    assert read_func(store, 0) == 42

    # Test 2: Write values and sum first 3
    write_func(store, 0, 10)
    write_func(store, 4, 20)
    write_func(store, 8, 30)

    # Verify individual values
    assert read_func(store, 0) == 10
    assert read_func(store, 4) == 20
    assert read_func(store, 8) == 30

    # Test sum function (sums values at addresses 0, 4, 8)
    total = sum_func(store, 3)  # parameter not used in simplified version
    assert total == 60  # 10 + 20 + 30 = 60


def test_global_state_modifications():
    """Test global variables and their modifications as side effects."""
    module = Module()

    # Type section
    get_counter_type = FuncType(params=[], results=[ValType.I32])
    increment_type = FuncType(params=[], results=[])
    add_to_counter_type = FuncType(params=[ValType.I32], results=[])
    reset_type = FuncType(params=[], results=[])

    type_section = TypeSection(
        types=[get_counter_type, increment_type, add_to_counter_type, reset_type]
    )
    module.add_section(type_section)

    # Function section
    function_section = FunctionSection(type_indices=[0, 1, 2, 3])
    module.add_section(function_section)

    # Global section - mutable counter (must come after function section)
    from wasmai.sections import GlobalSection

    counter_global = Global(
        global_type=GlobalType(val_type=ValType.I32, mutable=True),
        init_expr=[
            ConstInstruction(opcode=Opcode.I32_CONST, value=0),
        ],
    )
    global_section = GlobalSection(globals=[counter_global])
    module.add_section(global_section)

    # Export section
    export_section = ExportSection(
        exports=[
            Export(name='get_counter', desc=FuncExportDesc(func_idx=0)),
            Export(name='increment', desc=FuncExportDesc(func_idx=1)),
            Export(name='add_to_counter', desc=FuncExportDesc(func_idx=2)),
            Export(name='reset', desc=FuncExportDesc(func_idx=3)),
            Export(name='counter', desc=GlobalExportDesc(global_idx=0)),
        ]
    )
    module.add_section(export_section)

    # Code section
    get_counter_func = Func(
        locals=[],
        body=[
            GlobalInstruction(opcode=Opcode.GLOBAL_GET, global_idx=0),
            Instruction(opcode=Opcode.RETURN),
        ],
    )

    increment_func = Func(
        locals=[],
        body=[
            GlobalInstruction(opcode=Opcode.GLOBAL_GET, global_idx=0),
            ConstInstruction(opcode=Opcode.I32_CONST, value=1),
            Instruction(opcode=Opcode.I32_ADD),
            GlobalInstruction(opcode=Opcode.GLOBAL_SET, global_idx=0),
            Instruction(opcode=Opcode.RETURN),
        ],
    )

    add_to_counter_func = Func(
        locals=[],
        body=[
            GlobalInstruction(opcode=Opcode.GLOBAL_GET, global_idx=0),
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),
            Instruction(opcode=Opcode.I32_ADD),
            GlobalInstruction(opcode=Opcode.GLOBAL_SET, global_idx=0),
            Instruction(opcode=Opcode.RETURN),
        ],
    )

    reset_func = Func(
        locals=[],
        body=[
            ConstInstruction(opcode=Opcode.I32_CONST, value=0),
            GlobalInstruction(opcode=Opcode.GLOBAL_SET, global_idx=0),
            Instruction(opcode=Opcode.RETURN),
        ],
    )

    code_section = CodeSection(
        funcs=[get_counter_func, increment_func, add_to_counter_func, reset_func]
    )
    module.add_section(code_section)

    # Execute and test global state changes
    binary_data = encode_binary(module)
    engine = wasmtime.Engine()
    wasmtime_module = wasmtime.Module(engine, binary_data)
    store = wasmtime.Store(engine)
    instance = wasmtime.Instance(store, wasmtime_module, [])

    get_counter = instance.exports(store)['get_counter']
    increment = instance.exports(store)['increment']
    add_to_counter = instance.exports(store)['add_to_counter']
    reset = instance.exports(store)['reset']
    counter_global = instance.exports(store)['counter']

    # Test initial state
    assert get_counter(store) == 0
    assert counter_global.value(store) == 0

    # Test increment
    increment(store)
    assert get_counter(store) == 1
    assert counter_global.value(store) == 1

    # Test multiple increments
    increment(store)
    increment(store)
    assert get_counter(store) == 3

    # Test add operation
    add_to_counter(store, 10)
    assert get_counter(store) == 13

    # Test reset
    reset(store)
    assert get_counter(store) == 0
    assert counter_global.value(store) == 0

    # Test sequence of operations
    add_to_counter(store, 5)
    increment(store)
    increment(store)
    add_to_counter(store, 3)
    assert get_counter(store) == 10  # 0 + 5 + 1 + 1 + 3 = 10


def test_recursive_function_with_stack_effects():
    """Test recursive factorial function to verify stack management."""
    module = Module()

    # Type section
    func_type = FuncType(params=[ValType.I32], results=[ValType.I32])
    type_section = TypeSection(types=[func_type])
    module.add_section(type_section)

    # Function section
    function_section = FunctionSection(type_indices=[0])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(
        exports=[Export(name='factorial', desc=FuncExportDesc(func_idx=0))]
    )
    module.add_section(export_section)

    # Code section - recursive factorial
    factorial_func = Func(
        locals=[],
        body=[
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),  # n
            ConstInstruction(opcode=Opcode.I32_CONST, value=2),
            Instruction(opcode=Opcode.I32_LT_S),  # n < 2
            IfInstruction(
                opcode=Opcode.IF,
                block_type=ValType.I32,
                then_instructions=[
                    ConstInstruction(opcode=Opcode.I32_CONST, value=1),  # return 1
                ],
                else_instructions=[
                    LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),  # n
                    LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),  # n
                    ConstInstruction(opcode=Opcode.I32_CONST, value=1),
                    Instruction(opcode=Opcode.I32_SUB),  # n - 1
                    CallInstruction(opcode=Opcode.CALL, func_idx=0),  # factorial(n-1)
                    Instruction(opcode=Opcode.I32_MUL),  # n * factorial(n-1)
                ],
            ),
            Instruction(opcode=Opcode.RETURN),
        ],
    )
    code_section = CodeSection(funcs=[factorial_func])
    module.add_section(code_section)

    # Execute and test
    binary_data = encode_binary(module)
    engine = wasmtime.Engine()
    wasmtime_module = wasmtime.Module(engine, binary_data)
    store = wasmtime.Store(engine)
    instance = wasmtime.Instance(store, wasmtime_module, [])
    factorial = instance.exports(store)['factorial']

    # Test factorial values
    expected_factorials = [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880]
    for i, expected in enumerate(expected_factorials):
        result = factorial(store, i)
        assert result == expected, f'factorial({i}) = {result}, expected {expected}'

    # Test that the function can handle multiple calls (stack cleanup)
    assert factorial(store, 5) == 120
    assert factorial(store, 4) == 24
    assert factorial(store, 6) == 720
