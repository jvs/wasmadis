from .module import Module
from .types import *
from .instructions import *
from .sections import *
from .binary_encoder import encode_binary, encode_uleb128, encode_sleb128, encode_f32, encode_f64, encode_string
from .text_encoder import encode_text

__version__ = '0.1.0'

# Main module and encoding functions
__all__ = [
    'Module',
    'encode_binary',
    'encode_text',
    
    # Binary encoding utilities
    'encode_uleb128',
    'encode_sleb128', 
    'encode_f32',
    'encode_f64',
    'encode_string',
    
    # Value types and enums
    'ValType',
    'PackedType',
    
    # Type system
    'RefType',
    'FuncType',
    'StructType',
    'ArrayType',
    'FieldType',
    'Limits',
    'MemType',
    'TableType',
    'GlobalType',
    'CompositeType',
    
    # Instruction opcodes
    'Opcode',
    'AtomicOpcode',
    'GCOpcode',
    
    # Instruction classes
    'Instruction',
    'ConstInstruction',
    'LocalInstruction',
    'GlobalInstruction',
    'CallInstruction',
    'CallIndirectInstruction',
    'ReturnCallInstruction',
    'ReturnCallIndirectInstruction',
    'BrInstruction',
    'BrTableInstruction',
    'BlockInstruction',
    'IfInstruction',
    'MemoryInstruction',
    'AtomicMemoryInstruction',
    'RefNullInstruction',
    'RefFuncInstruction',
    'StructNewInstruction',
    'StructGetInstruction',
    'StructSetInstruction',
    'ArrayNewInstruction',
    'ArrayGetInstruction',
    'ArraySetInstruction',
    'ArrayNewFixedInstruction',
    'RefTestInstruction',
    'RefCastInstruction',
    'BrOnCastInstruction',
    
    # Sections
    'SectionId',
    'Section',
    'CustomSection',
    'TypeSection',
    'ImportSection',
    'FunctionSection',
    'TableSection',
    'MemorySection',
    'GlobalSection',
    'ExportSection',
    'StartSection',
    'ElementSection',
    'CodeSection',
    'DataSection',
    'DataCountSection',
    
    # Import/Export descriptors
    'ImportDesc',
    'ExportDesc',
    'FuncImportDesc',
    'TableImportDesc',
    'MemImportDesc',
    'GlobalImportDesc',
    'FuncExportDesc',
    'TableExportDesc',
    'MemExportDesc',
    'GlobalExportDesc',
    
    # Helper classes
    'Import',
    'Export',
    'Table',
    'Memory',
    'Global',
    'Element',
    'Func',
    'Locals',
    'Data',
    
    # Element and data modes
    'ElementMode',
    'DataMode',
    'PassiveElementMode',
    'ActiveElementMode',
    'DeclarativeElementMode',
    'PassiveDataMode',
    'ActiveDataMode',
]
