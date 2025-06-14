#!/usr/bin/env python3
"""
Demonstration of the simplified wasmadis API.
All classes and functions are available directly from the main package.
"""

# Everything you need in one import!
from wasmadis import *


def main():
    print('🚀 wasmadis API Demo - Simplified Imports')
    print('=' * 50)

    # Create a module that demonstrates various WASM 2.0 features
    module = Module()

    # 1. Add type definitions
    func_type = FuncType(params=[ValType.I32], results=[ValType.I32])
    struct_type = StructType(
        fields=[
            FieldType(storage_type=ValType.I32, mutable=False),
            FieldType(storage_type=ValType.F32, mutable=True),
        ]
    )
    type_section = TypeSection(types=[func_type, struct_type])
    module.add_section(type_section)

    # 2. Add functions
    function_section = FunctionSection(type_indices=[0])
    module.add_section(function_section)

    # 3. Add exports
    export_section = ExportSection(
        exports=[Export(name='bit_count', desc=FuncExportDesc(func_idx=0))]
    )
    module.add_section(export_section)

    # 4. Add code with new WASM 2.0 instructions
    func = Func(
        locals=[],
        body=[
            # Get input parameter
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),
            # Use new bit manipulation instructions
            Instruction(opcode=Opcode.I32_POPCNT),  # Count set bits
            LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),
            Instruction(opcode=Opcode.I32_CLZ),  # Count leading zeros
            Instruction(opcode=Opcode.I32_ADD),  # Add them together
            # Return result
            Instruction(opcode=Opcode.RETURN),
        ],
    )
    code_section = CodeSection(funcs=[func])
    module.add_section(code_section)

    # 5. Generate outputs
    print('📝 Generated WebAssembly Text (WAT):')
    wat = encode_text(module)
    print(wat)

    binary = encode_binary(module)
    print(f'📦 Binary module size: {len(binary)} bytes')

    # 6. Show available opcodes
    print(f'\n🎯 Available instruction opcodes: {len(Opcode)} standard')
    print(f'⚛️  Atomic opcodes: {len(AtomicOpcode)}')
    print(f'🗑️  GC opcodes: {len(GCOpcode)}')

    # 7. Demonstrate other features
    print(f'\n🔧 Value types: {[t.name for t in ValType]}')
    print(f'📂 Section types: {[t.name for t in SectionId]}')

    print('\n✅ All features accessible from a single import!')
    print('   No more complex subpackage imports needed!')


if __name__ == '__main__':
    main()
