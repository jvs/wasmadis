# wasmadis

Python dataclasses for representing WASM modules with WASM 2.0, GC, threads, and tail call support.

## Features

- **Complete WASM 2.0 support**: Reference types, function references, and extended type system
- **GC proposal**: Struct types, array types, i31ref, and all GC instructions
- **Threads proposal**: Shared memory and atomic operations
- **Tail call proposal**: Return call instructions for optimized recursion
- **Binary encoding**: Generate valid WASM binary modules
- **Text encoding**: Generate WAT (WebAssembly Text) format
- **Wasmtime validation**: All generated modules are validated with wasmtime-py

## Installation

```bash
uv add wasmadis
```

For development:

```bash
git clone <repo>
cd wasmadis
uv sync --dev
```

## Quick Start

```python
from wasmadis import Module, encode_binary, encode_text
from wasmadis.types import FuncType, ValType
from wasmadis.sections import TypeSection, FunctionSection, ExportSection, CodeSection
from wasmadis.sections import Export, FuncExportDesc, Func
from wasmadis.instructions import LocalInstruction, Instruction, Opcode

# Create a simple add function
module = Module()

# Type section
func_type = FuncType(params=[ValType.I32, ValType.I32], results=[ValType.I32])
type_section = TypeSection(types=[func_type])
module.add_section(type_section)

# Function section
function_section = FunctionSection(type_indices=[0])
module.add_section(function_section)

# Export section
export_section = ExportSection(exports=[
    Export(name='add', desc=FuncExportDesc(func_idx=0))
])
module.add_section(export_section)

# Code section
add_func = Func(
    locals=[],
    body=[
        LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=0),
        LocalInstruction(opcode=Opcode.LOCAL_GET, local_idx=1),
        Instruction(opcode=Opcode.I32_ADD),
        Instruction(opcode=Opcode.RETURN),
    ]
)
code_section = CodeSection(funcs=[add_func])
module.add_section(code_section)

# Generate binary WASM
binary_data = encode_binary(module)

# Generate WAT text
wat_text = encode_text(module)
print(wat_text)
```

## Advanced Features

### GC Types

```python
from wasmadis.types import StructType, FieldType
from wasmadis.instructions import StructNewInstruction, GCOpcode

# Create a struct type
person_struct = StructType(fields=[
    FieldType(storage_type=ValType.I32, mutable=False),  # age
    FieldType(storage_type=ValType.I32, mutable=True)    # score
])

# Use in instructions
struct_new = StructNewInstruction(opcode=GCOpcode.STRUCT_NEW, type_idx=0)
```

### Atomic Operations

```python
from wasmadis.instructions import AtomicMemoryInstruction, AtomicOpcode
from wasmadis.types import Limits, MemType

# Shared memory
shared_memory = Memory(mem_type=MemType(limits=Limits(min=1, max=1, shared=True)))

# Atomic instruction
atomic_add = AtomicMemoryInstruction(
    opcode=AtomicOpcode.I32_ATOMIC_RMW_ADD, 
    align=2, 
    offset=0
)
```

### Tail Calls

```python
from wasmadis.instructions import ReturnCallInstruction

# Tail call
tail_call = ReturnCallInstruction(opcode=Opcode.RETURN_CALL, func_idx=1)
```

## Development

This project uses [just](https://github.com/casey/just) for convenient development commands:

```bash
# Run all tests
just test

# Run tests with coverage analysis
just test-cov

# Show coverage report
just coverage-report

# Generate HTML coverage report
just coverage-html

# Format code with ruff (single quotes)
just fmt

# Check code with ruff linter
just lint

# Run both formatter and linter
just check

# Run the example script
just example

# Generate WAT and WASM files from examples
just generate-wat

# Run a quick smoke test
just smoke

# Show all available commands
just help
```

You can also run commands directly with uv:

```bash
uv run pytest          # Run tests
uv run ruff format .   # Format code
uv run ruff check .    # Lint code
```

## License

MIT