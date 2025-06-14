#!/usr/bin/env python3

# Simple import - everything available from main package
from wasmadis import *


def create_simple_module():
    module = Module()

    # Type section with function type
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

    return module


def create_gc_module():
    module = Module()

    # Type section with struct type
    person_struct = StructType(
        fields=[
            FieldType(storage_type=ValType.I32, mutable=False),  # age
            FieldType(storage_type=ValType.I32, mutable=True),  # score
        ]
    )
    func_type = FuncType(params=[], results=[ValType.ANYREF])

    type_section = TypeSection(types=[person_struct, func_type])
    module.add_section(type_section)

    # Function section
    function_section = FunctionSection(type_indices=[1])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(
        exports=[Export(name='create_person', desc=FuncExportDesc(func_idx=0))]
    )
    module.add_section(export_section)

    # Code section with GC instructions
    create_person_func = Func(
        locals=[],
        body=[
            ConstInstruction(opcode=Opcode.I32_CONST, value=25),  # age = 25
            ConstInstruction(opcode=Opcode.I32_CONST, value=100),  # score = 100
            StructNewInstruction(opcode=GCOpcode.STRUCT_NEW, type_idx=0),
            Instruction(opcode=Opcode.RETURN),
        ],
    )
    code_section = CodeSection(funcs=[create_person_func])
    module.add_section(code_section)

    return module


def create_threads_module():
    module = Module()

    # Type section
    func_type = FuncType(params=[ValType.I32], results=[ValType.I32])
    type_section = TypeSection(types=[func_type])
    module.add_section(type_section)

    # Memory section with shared memory
    shared_memory = Memory(mem_type=MemType(limits=Limits(min=1, max=1, shared=True)))
    memory_section = MemorySection(memories=[shared_memory])
    module.add_section(memory_section)

    # Function section
    function_section = FunctionSection(type_indices=[0])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(
        exports=[
            Export(name='atomic_add', desc=FuncExportDesc(func_idx=0)),
            Export(name='memory', desc=MemExportDesc(mem_idx=0)),
        ]
    )
    module.add_section(export_section)

    # Code section with atomic operations
    atomic_add_func = Func(
        locals=[],
        body=[
            ConstInstruction(opcode=Opcode.I32_CONST, value=0),  # memory address
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),  # value to add
            AtomicMemoryInstruction(opcode=AtomicOpcode.I32_ATOMIC_RMW_ADD, align=2, offset=0),
            Instruction(opcode=Opcode.RETURN),
        ],
    )
    code_section = CodeSection(funcs=[atomic_add_func])
    module.add_section(code_section)

    return module


def create_tail_call_module():
    module = Module()

    # Type section
    func_type = FuncType(params=[ValType.I32], results=[ValType.I32])
    type_section = TypeSection(types=[func_type])
    module.add_section(type_section)

    # Function section - two functions for mutual recursion
    function_section = FunctionSection(type_indices=[0, 0])
    module.add_section(function_section)

    # Export section
    export_section = ExportSection(
        exports=[Export(name='factorial', desc=FuncExportDesc(func_idx=0))]
    )
    module.add_section(export_section)

    # Code section with tail call
    factorial_func = Func(
        locals=[],
        body=[
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),
            ConstInstruction(opcode=Opcode.I32_CONST, value=1),
            Instruction(opcode=Opcode.I32_LE_S),
            IfInstruction(
                opcode=Opcode.IF,
                block_type=ValType.I32,
                then_instructions=[
                    ConstInstruction(opcode=Opcode.I32_CONST, value=1),
                    Instruction(opcode=Opcode.RETURN),
                ],
            ),
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),
            ConstInstruction(opcode=Opcode.I32_CONST, value=1),
            Instruction(opcode=Opcode.I32_SUB),
            ReturnCallInstruction(opcode=Opcode.RETURN_CALL, func_idx=1),
        ],
    )

    helper_func = Func(
        locals=[],
        body=[
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=1),
            Instruction(opcode=Opcode.I32_MUL),
            Instruction(opcode=Opcode.RETURN),
        ],
    )

    code_section = CodeSection(funcs=[factorial_func, helper_func])
    module.add_section(code_section)

    return module


def main():
    print('Creating WASM modules with different features...')

    # Simple module
    print('\n1. Simple add function:')
    simple_module = create_simple_module()
    simple_wat = encode_text(simple_module)
    print(simple_wat)

    simple_binary = encode_binary(simple_module)
    print(f'Binary size: {len(simple_binary)} bytes')

    # GC module
    print('\n2. GC module with struct:')
    gc_module = create_gc_module()
    gc_wat = encode_text(gc_module)
    print(gc_wat)

    # Threads module
    print('\n3. Threads module with shared memory:')
    threads_module = create_threads_module()
    threads_wat = encode_text(threads_module)
    print(threads_wat)

    # Tail call module
    print('\n4. Tail call module:')
    tail_call_module = create_tail_call_module()
    tail_call_wat = encode_text(tail_call_module)
    print(tail_call_wat)

    print('\nAll modules created successfully!')


if __name__ == '__main__':
    main()
