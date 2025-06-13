import struct
from typing import List, Union
from .module import Module
from .sections import *
from .types import *
from .instructions import *


def encode_uleb128(value: int) -> bytes:
    result = []
    while value >= 0x80:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value & 0x7F)
    return bytes(result)


def encode_sleb128(value: int) -> bytes:
    result = []
    while True:
        byte = value & 0x7F
        value >>= 7
        if (value == 0 and (byte & 0x40) == 0) or (value == -1 and (byte & 0x40) != 0):
            result.append(byte)
            break
        result.append(byte | 0x80)
    return bytes(result)


def encode_f32(value: float) -> bytes:
    return struct.pack('<f', value)


def encode_f64(value: float) -> bytes:
    return struct.pack('<d', value)


def encode_string(s: str) -> bytes:
    encoded = s.encode('utf-8')
    return encode_uleb128(len(encoded)) + encoded


def encode_vector(items: List, encode_item) -> bytes:
    result = encode_uleb128(len(items))
    for item in items:
        result += encode_item(item)
    return result


def encode_valtype(valtype: ValType) -> bytes:
    return bytes([valtype.value])


def encode_reftype(reftype: RefType) -> bytes:
    result = b''
    if reftype.nullable:
        result += bytes(
            [
                0x6F
                if isinstance(reftype.heap_type, ValType) and reftype.heap_type == ValType.EXTERNREF
                else 0x70
            ]
        )
    else:
        result += bytes(
            [
                0x72
                if isinstance(reftype.heap_type, ValType) and reftype.heap_type == ValType.EXTERNREF
                else 0x73
            ]
        )

    if isinstance(reftype.heap_type, int):
        result += encode_sleb128(reftype.heap_type)
    elif isinstance(reftype.heap_type, ValType):
        result += encode_valtype(reftype.heap_type)

    return result


def encode_functype(functype: FuncType) -> bytes:
    result = bytes([0x60])
    result += encode_vector(functype.params, encode_valtype)
    result += encode_vector(functype.results, encode_valtype)
    return result


def encode_structtype(structtype: StructType) -> bytes:
    result = bytes([0x5F])
    result += encode_vector(structtype.fields, encode_fieldtype)
    return result


def encode_arraytype(arraytype: ArrayType) -> bytes:
    result = bytes([0x5E])
    result += encode_fieldtype(arraytype.element_type)
    return result


def encode_fieldtype(fieldtype: FieldType) -> bytes:
    result = b''
    if isinstance(fieldtype.storage_type, ValType):
        result += encode_valtype(fieldtype.storage_type)
    elif isinstance(fieldtype.storage_type, PackedType):
        result += bytes([fieldtype.storage_type.value])

    result += bytes([0x01 if fieldtype.mutable else 0x00])
    return result


def encode_limits(limits: Limits) -> bytes:
    if limits.max is None:
        if limits.shared:
            return bytes([0x03]) + encode_uleb128(limits.min)
        else:
            return bytes([0x00]) + encode_uleb128(limits.min)
    else:
        if limits.shared:
            return bytes([0x03]) + encode_uleb128(limits.min) + encode_uleb128(limits.max)
        else:
            return bytes([0x01]) + encode_uleb128(limits.min) + encode_uleb128(limits.max)


def encode_memtype(memtype: MemType) -> bytes:
    return encode_limits(memtype.limits)


def encode_tabletype(tabletype: TableType) -> bytes:
    return encode_reftype(tabletype.element_type) + encode_limits(tabletype.limits)


def encode_globaltype(globaltype: GlobalType) -> bytes:
    return encode_valtype(globaltype.val_type) + bytes([0x01 if globaltype.mutable else 0x00])


def encode_instruction(instr: Instruction) -> bytes:
    result = b''

    if isinstance(instr.opcode, Opcode):
        result += bytes([instr.opcode.value])
    elif isinstance(instr.opcode, AtomicOpcode):
        result += bytes([0xFE]) + encode_uleb128(instr.opcode.value & 0xFF)
    elif isinstance(instr.opcode, GCOpcode):
        result += bytes([0xFB]) + encode_uleb128(instr.opcode.value & 0xFF)

    if isinstance(instr, ConstInstruction):
        if instr.opcode in [Opcode.I32_CONST, Opcode.I64_CONST]:
            result += encode_sleb128(int(instr.value))
        elif instr.opcode == Opcode.F32_CONST:
            result += encode_f32(float(instr.value))
        elif instr.opcode == Opcode.F64_CONST:
            result += encode_f64(float(instr.value))
    elif isinstance(instr, LocalInstruction):
        result += encode_uleb128(instr.local_idx)
    elif isinstance(instr, GlobalInstruction):
        result += encode_uleb128(instr.global_idx)
    elif isinstance(instr, CallInstruction):
        result += encode_uleb128(instr.func_idx)
    elif isinstance(instr, CallIndirectInstruction):
        result += encode_uleb128(instr.type_idx)
        result += encode_uleb128(instr.table_idx)
    elif isinstance(instr, ReturnCallInstruction):
        result += encode_uleb128(instr.func_idx)
    elif isinstance(instr, ReturnCallIndirectInstruction):
        result += encode_uleb128(instr.type_idx)
        result += encode_uleb128(instr.table_idx)
    elif isinstance(instr, BrInstruction):
        result += encode_uleb128(instr.label_idx)
    elif isinstance(instr, BrTableInstruction):
        result += encode_vector(instr.label_indices, encode_uleb128)
        result += encode_uleb128(instr.default_label)
    elif isinstance(instr, BlockInstruction):
        if instr.block_type is None:
            result += bytes([0x40])
        elif isinstance(instr.block_type, ValType):
            result += encode_valtype(instr.block_type)
        else:
            result += encode_sleb128(instr.block_type)
        result += encode_vector(instr.instructions, encode_instruction)
        result += bytes([0x0B])
    elif isinstance(instr, IfInstruction):
        if instr.block_type is None:
            result += bytes([0x40])
        elif isinstance(instr.block_type, ValType):
            result += encode_valtype(instr.block_type)
        else:
            result += encode_sleb128(instr.block_type)
        for then_instr in instr.then_instructions:
            result += encode_instruction(then_instr)
        if instr.else_instructions:
            result += bytes([0x05])
            for else_instr in instr.else_instructions:
                result += encode_instruction(else_instr)
        result += bytes([0x0B])
    elif isinstance(instr, MemoryInstruction):
        result += encode_uleb128(instr.align)
        result += encode_uleb128(instr.offset)
    elif isinstance(instr, AtomicMemoryInstruction):
        result += encode_uleb128(instr.align)
        result += encode_uleb128(instr.offset)
    elif isinstance(instr, RefNullInstruction):
        result += encode_reftype(instr.ref_type)
    elif isinstance(instr, RefFuncInstruction):
        result += encode_uleb128(instr.func_idx)
    elif isinstance(instr, StructNewInstruction):
        result += encode_uleb128(instr.type_idx)
    elif isinstance(instr, StructGetInstruction):
        result += encode_uleb128(instr.type_idx)
        result += encode_uleb128(instr.field_idx)
    elif isinstance(instr, StructSetInstruction):
        result += encode_uleb128(instr.type_idx)
        result += encode_uleb128(instr.field_idx)
    elif isinstance(instr, ArrayNewInstruction):
        result += encode_uleb128(instr.type_idx)
    elif isinstance(instr, ArrayGetInstruction):
        result += encode_uleb128(instr.type_idx)
    elif isinstance(instr, ArraySetInstruction):
        result += encode_uleb128(instr.type_idx)
    elif isinstance(instr, ArrayNewFixedInstruction):
        result += encode_uleb128(instr.type_idx)
        result += encode_uleb128(instr.size)
    elif isinstance(instr, RefTestInstruction):
        result += encode_reftype(instr.ref_type)
    elif isinstance(instr, RefCastInstruction):
        result += encode_reftype(instr.ref_type)
    elif isinstance(instr, BrOnCastInstruction):
        result += encode_uleb128(instr.label_idx)
        result += encode_reftype(instr.ref_type_from)
        result += encode_reftype(instr.ref_type_to)

    return result


def encode_expr(instructions: List[Instruction]) -> bytes:
    result = b''
    for instr in instructions:
        result += encode_instruction(instr)
    result += bytes([0x0B])
    return result


def encode_section(section: Section) -> bytes:
    section_data = b''

    if isinstance(section, CustomSection):
        section_data = encode_string(section.name) + section.data
    elif isinstance(section, TypeSection):

        def encode_composite_type(t):
            if isinstance(t, FuncType):
                return encode_functype(t)
            elif isinstance(t, StructType):
                return encode_structtype(t)
            elif isinstance(t, ArrayType):
                return encode_arraytype(t)
            return b''

        section_data = encode_vector(section.types, encode_composite_type)
    elif isinstance(section, ImportSection):

        def encode_import(imp):
            result = encode_string(imp.module) + encode_string(imp.name)
            if isinstance(imp.desc, FuncImportDesc):
                result += bytes([0x00]) + encode_uleb128(imp.desc.type_idx)
            elif isinstance(imp.desc, TableImportDesc):
                result += bytes([0x01]) + encode_tabletype(imp.desc.table_type)
            elif isinstance(imp.desc, MemImportDesc):
                result += bytes([0x02]) + encode_memtype(imp.desc.mem_type)
            elif isinstance(imp.desc, GlobalImportDesc):
                result += bytes([0x03]) + encode_globaltype(imp.desc.global_type)
            return result

        section_data = encode_vector(section.imports, encode_import)
    elif isinstance(section, FunctionSection):
        section_data = encode_vector(section.type_indices, encode_uleb128)
    elif isinstance(section, TableSection):

        def encode_table(table):
            return encode_tabletype(table.table_type)

        section_data = encode_vector(section.tables, encode_table)
    elif isinstance(section, MemorySection):

        def encode_memory(memory):
            return encode_memtype(memory.mem_type)

        section_data = encode_vector(section.memories, encode_memory)
    elif isinstance(section, GlobalSection):

        def encode_global(glob):
            return encode_globaltype(glob.global_type) + encode_expr(glob.init_expr)

        section_data = encode_vector(section.globals, encode_global)
    elif isinstance(section, ExportSection):

        def encode_export(exp):
            result = encode_string(exp.name)
            if isinstance(exp.desc, FuncExportDesc):
                result += bytes([0x00]) + encode_uleb128(exp.desc.func_idx)
            elif isinstance(exp.desc, TableExportDesc):
                result += bytes([0x01]) + encode_uleb128(exp.desc.table_idx)
            elif isinstance(exp.desc, MemExportDesc):
                result += bytes([0x02]) + encode_uleb128(exp.desc.mem_idx)
            elif isinstance(exp.desc, GlobalExportDesc):
                result += bytes([0x03]) + encode_uleb128(exp.desc.global_idx)
            return result

        section_data = encode_vector(section.exports, encode_export)
    elif isinstance(section, StartSection):
        section_data = encode_uleb128(section.func_idx)
    elif isinstance(section, ElementSection):

        def encode_element(elem):
            result = b''
            if isinstance(elem.mode, PassiveElementMode):
                result += bytes([0x01])
                result += encode_reftype(elem.ref_type)
            elif isinstance(elem.mode, ActiveElementMode):
                result += bytes([0x00])
                result += encode_expr(elem.mode.offset_expr)
            elif isinstance(elem.mode, DeclarativeElementMode):
                result += bytes([0x03])
                result += encode_reftype(elem.ref_type)

            result += encode_vector(elem.init_exprs, encode_expr)
            return result

        section_data = encode_vector(section.elements, encode_element)
    elif isinstance(section, CodeSection):

        def encode_func(func):
            func_data = encode_vector(
                func.locals, lambda l: encode_uleb128(l.count) + encode_valtype(l.val_type)
            )
            func_data += encode_expr(func.body)
            return encode_uleb128(len(func_data)) + func_data

        section_data = encode_vector(section.funcs, encode_func)
    elif isinstance(section, DataSection):

        def encode_data(data):
            result = b''
            if isinstance(data.mode, PassiveDataMode):
                result += bytes([0x01])
            elif isinstance(data.mode, ActiveDataMode):
                result += bytes([0x00])
                result += encode_expr(data.mode.offset_expr)

            result += encode_vector(list(data.init), lambda b: bytes([b]))
            return result

        section_data = encode_vector(section.data, encode_data)
    elif isinstance(section, DataCountSection):
        section_data = encode_uleb128(section.count)

    return bytes([section.id.value]) + encode_uleb128(len(section_data)) + section_data


def encode_binary(module: Module) -> bytes:
    result = b'\x00asm'
    result += struct.pack('<I', module.version)

    for section in module.sections:
        result += encode_section(section)

    return result
