from .module import Module
from .sections import *
from .types import *
from .instructions import *


def indent(text: str, level: int = 1) -> str:
    return '\n'.join('  ' * level + line if line.strip() else line for line in text.split('\n'))


def format_valtype(valtype: ValType) -> str:
    type_map = {
        ValType.I32: 'i32',
        ValType.I64: 'i64',
        ValType.F32: 'f32',
        ValType.F64: 'f64',
        ValType.V128: 'v128',
        ValType.FUNCREF: 'funcref',
        ValType.EXTERNREF: 'externref',
        ValType.ANYREF: 'anyref',
        ValType.EQREF: 'eqref',
        ValType.I31REF: 'i31ref',
        ValType.STRUCTREF: 'structref',
        ValType.ARRAYREF: 'arrayref',
        ValType.NULLFUNCREF: 'nullfuncref',
        ValType.NULLEXTERNREF: 'nullexternref',
        ValType.NULLREF: 'nullref',
    }
    return type_map.get(valtype, str(valtype))


def format_reftype(reftype: RefType) -> str:
    nullable = '' if reftype.nullable else 'nonnull '
    if isinstance(reftype.heap_type, ValType):
        return f'{nullable}{format_valtype(reftype.heap_type)}'
    else:
        return f'{nullable}(ref {reftype.heap_type})'


def format_functype(functype: FuncType) -> str:
    params = ' '.join(f'(param {format_valtype(p)})' for p in functype.params)
    results = ' '.join(f'(result {format_valtype(r)})' for r in functype.results)
    return f'(func {params} {results})'


def format_structtype(structtype: StructType) -> str:
    fields = []
    for i, field in enumerate(structtype.fields):
        mut = '(mut ' if field.mutable else ''
        end = ')' if field.mutable else ''
        if isinstance(field.storage_type, ValType):
            fields.append(f'(field {mut}{format_valtype(field.storage_type)}{end})')
        elif isinstance(field.storage_type, PackedType):
            pack_type = 'i8' if field.storage_type == PackedType.I8 else 'i16'
            fields.append(f'(field {mut}{pack_type}{end})')
    return f'(struct {" ".join(fields)})'


def format_arraytype(arraytype: ArrayType) -> str:
    mut = '(mut ' if arraytype.element_type.mutable else ''
    end = ')' if arraytype.element_type.mutable else ''
    if isinstance(arraytype.element_type.storage_type, ValType):
        elem_type = format_valtype(arraytype.element_type.storage_type)
    else:
        elem_type = 'i8' if arraytype.element_type.storage_type == PackedType.I8 else 'i16'
    return f'(array {mut}{elem_type}{end})'


def format_limits(limits: Limits) -> str:
    shared = ' shared' if limits.shared else ''
    if limits.max is None:
        return f'{limits.min}{shared}'
    return f'{limits.min} {limits.max}{shared}'


def format_memtype(memtype: MemType) -> str:
    return format_limits(memtype.limits)


def format_tabletype(tabletype: TableType) -> str:
    return f'{format_limits(tabletype.limits)} {format_reftype(tabletype.element_type)}'


def format_globaltype(globaltype: GlobalType) -> str:
    mut = '(mut ' if globaltype.mutable else ''
    end = ')' if globaltype.mutable else ''
    return f'{mut}{format_valtype(globaltype.val_type)}{end}'


def format_instruction(instr: Instruction, indent_level: int = 0) -> str:
    opcode_map = {
        Opcode.UNREACHABLE: 'unreachable',
        Opcode.NOP: 'nop',
        Opcode.BLOCK: 'block',
        Opcode.LOOP: 'loop',
        Opcode.IF: 'if',
        Opcode.ELSE: 'else',
        Opcode.END: 'end',
        Opcode.BR: 'br',
        Opcode.BR_IF: 'br_if',
        Opcode.BR_TABLE: 'br_table',
        Opcode.RETURN: 'return',
        Opcode.CALL: 'call',
        Opcode.CALL_INDIRECT: 'call_indirect',
        Opcode.RETURN_CALL: 'return_call',
        Opcode.RETURN_CALL_INDIRECT: 'return_call_indirect',
        Opcode.DROP: 'drop',
        Opcode.SELECT: 'select',
        Opcode.SELECT_T: 'select',
        Opcode.LOCAL_GET: 'local.get',
        Opcode.LOCAL_SET: 'local.set',
        Opcode.LOCAL_TEE: 'local.tee',
        Opcode.GLOBAL_GET: 'global.get',
        Opcode.GLOBAL_SET: 'global.set',
        Opcode.TABLE_GET: 'table.get',
        Opcode.TABLE_SET: 'table.set',
        Opcode.I32_LOAD: 'i32.load',
        Opcode.I64_LOAD: 'i64.load',
        Opcode.F32_LOAD: 'f32.load',
        Opcode.F64_LOAD: 'f64.load',
        Opcode.I32_LOAD8_S: 'i32.load8_s',
        Opcode.I32_LOAD8_U: 'i32.load8_u',
        Opcode.I32_LOAD16_S: 'i32.load16_s',
        Opcode.I32_LOAD16_U: 'i32.load16_u',
        Opcode.I64_LOAD8_S: 'i64.load8_s',
        Opcode.I64_LOAD8_U: 'i64.load8_u',
        Opcode.I64_LOAD16_S: 'i64.load16_s',
        Opcode.I64_LOAD16_U: 'i64.load16_u',
        Opcode.I64_LOAD32_S: 'i64.load32_s',
        Opcode.I64_LOAD32_U: 'i64.load32_u',
        Opcode.I32_STORE: 'i32.store',
        Opcode.I64_STORE: 'i64.store',
        Opcode.F32_STORE: 'f32.store',
        Opcode.F64_STORE: 'f64.store',
        Opcode.I32_STORE8: 'i32.store8',
        Opcode.I32_STORE16: 'i32.store16',
        Opcode.I64_STORE8: 'i64.store8',
        Opcode.I64_STORE16: 'i64.store16',
        Opcode.I64_STORE32: 'i64.store32',
        Opcode.MEMORY_SIZE: 'memory.size',
        Opcode.MEMORY_GROW: 'memory.grow',
        Opcode.MEMORY_COPY: 'memory.copy',
        Opcode.MEMORY_FILL: 'memory.fill',
        Opcode.I32_CONST: 'i32.const',
        Opcode.I64_CONST: 'i64.const',
        Opcode.F32_CONST: 'f32.const',
        Opcode.F64_CONST: 'f64.const',
        Opcode.I32_EQZ: 'i32.eqz',
        Opcode.I32_EQ: 'i32.eq',
        Opcode.I32_NE: 'i32.ne',
        Opcode.I32_LT_S: 'i32.lt_s',
        Opcode.I32_LT_U: 'i32.lt_u',
        Opcode.I32_GT_S: 'i32.gt_s',
        Opcode.I32_GT_U: 'i32.gt_u',
        Opcode.I32_LE_S: 'i32.le_s',
        Opcode.I32_LE_U: 'i32.le_u',
        Opcode.I32_GE_S: 'i32.ge_s',
        Opcode.I32_GE_U: 'i32.ge_u',
        Opcode.I64_EQZ: 'i64.eqz',
        Opcode.I64_EQ: 'i64.eq',
        Opcode.I64_NE: 'i64.ne',
        Opcode.I64_LT_S: 'i64.lt_s',
        Opcode.I64_LT_U: 'i64.lt_u',
        Opcode.I64_GT_S: 'i64.gt_s',
        Opcode.I64_GT_U: 'i64.gt_u',
        Opcode.I64_LE_S: 'i64.le_s',
        Opcode.I64_LE_U: 'i64.le_u',
        Opcode.I64_GE_S: 'i64.ge_s',
        Opcode.I64_GE_U: 'i64.ge_u',
        Opcode.F32_EQ: 'f32.eq',
        Opcode.F32_NE: 'f32.ne',
        Opcode.F32_LT: 'f32.lt',
        Opcode.F32_GT: 'f32.gt',
        Opcode.F32_LE: 'f32.le',
        Opcode.F32_GE: 'f32.ge',
        Opcode.F64_EQ: 'f64.eq',
        Opcode.F64_NE: 'f64.ne',
        Opcode.F64_LT: 'f64.lt',
        Opcode.F64_GT: 'f64.gt',
        Opcode.F64_LE: 'f64.le',
        Opcode.F64_GE: 'f64.ge',
        Opcode.I32_CLZ: 'i32.clz',
        Opcode.I32_CTZ: 'i32.ctz',
        Opcode.I32_POPCNT: 'i32.popcnt',
        Opcode.I32_ADD: 'i32.add',
        Opcode.I32_SUB: 'i32.sub',
        Opcode.I32_MUL: 'i32.mul',
        Opcode.I32_DIV_S: 'i32.div_s',
        Opcode.I32_DIV_U: 'i32.div_u',
        Opcode.I32_REM_S: 'i32.rem_s',
        Opcode.I32_REM_U: 'i32.rem_u',
        Opcode.I32_AND: 'i32.and',
        Opcode.I32_OR: 'i32.or',
        Opcode.I32_XOR: 'i32.xor',
        Opcode.I32_SHL: 'i32.shl',
        Opcode.I32_SHR_S: 'i32.shr_s',
        Opcode.I32_SHR_U: 'i32.shr_u',
        Opcode.I32_ROTL: 'i32.rotl',
        Opcode.I32_ROTR: 'i32.rotr',
        Opcode.I64_CLZ: 'i64.clz',
        Opcode.I64_CTZ: 'i64.ctz',
        Opcode.I64_POPCNT: 'i64.popcnt',
        Opcode.I64_ADD: 'i64.add',
        Opcode.I64_SUB: 'i64.sub',
        Opcode.I64_MUL: 'i64.mul',
        Opcode.I64_DIV_S: 'i64.div_s',
        Opcode.I64_DIV_U: 'i64.div_u',
        Opcode.I64_REM_S: 'i64.rem_s',
        Opcode.I64_REM_U: 'i64.rem_u',
        Opcode.I64_AND: 'i64.and',
        Opcode.I64_OR: 'i64.or',
        Opcode.I64_XOR: 'i64.xor',
        Opcode.I64_SHL: 'i64.shl',
        Opcode.I64_SHR_S: 'i64.shr_s',
        Opcode.I64_SHR_U: 'i64.shr_u',
        Opcode.I64_ROTL: 'i64.rotl',
        Opcode.I64_ROTR: 'i64.rotr',
        Opcode.F32_ABS: 'f32.abs',
        Opcode.F32_NEG: 'f32.neg',
        Opcode.F32_CEIL: 'f32.ceil',
        Opcode.F32_FLOOR: 'f32.floor',
        Opcode.F32_TRUNC: 'f32.trunc',
        Opcode.F32_NEAREST: 'f32.nearest',
        Opcode.F32_SQRT: 'f32.sqrt',
        Opcode.F32_ADD: 'f32.add',
        Opcode.F32_SUB: 'f32.sub',
        Opcode.F32_MUL: 'f32.mul',
        Opcode.F32_DIV: 'f32.div',
        Opcode.F32_MIN: 'f32.min',
        Opcode.F32_MAX: 'f32.max',
        Opcode.F32_COPYSIGN: 'f32.copysign',
        Opcode.F64_ABS: 'f64.abs',
        Opcode.F64_NEG: 'f64.neg',
        Opcode.F64_CEIL: 'f64.ceil',
        Opcode.F64_FLOOR: 'f64.floor',
        Opcode.F64_TRUNC: 'f64.trunc',
        Opcode.F64_NEAREST: 'f64.nearest',
        Opcode.F64_SQRT: 'f64.sqrt',
        Opcode.F64_ADD: 'f64.add',
        Opcode.F64_SUB: 'f64.sub',
        Opcode.F64_MUL: 'f64.mul',
        Opcode.F64_DIV: 'f64.div',
        Opcode.F64_MIN: 'f64.min',
        Opcode.F64_MAX: 'f64.max',
        Opcode.F64_COPYSIGN: 'f64.copysign',
        Opcode.I32_WRAP_I64: 'i32.wrap_i64',
        Opcode.I32_TRUNC_F32_S: 'i32.trunc_f32_s',
        Opcode.I32_TRUNC_F32_U: 'i32.trunc_f32_u',
        Opcode.I32_TRUNC_F64_S: 'i32.trunc_f64_s',
        Opcode.I32_TRUNC_F64_U: 'i32.trunc_f64_u',
        Opcode.I64_EXTEND_I32_S: 'i64.extend_i32_s',
        Opcode.I64_EXTEND_I32_U: 'i64.extend_i32_u',
        Opcode.I64_TRUNC_F32_S: 'i64.trunc_f32_s',
        Opcode.I64_TRUNC_F32_U: 'i64.trunc_f32_u',
        Opcode.I64_TRUNC_F64_S: 'i64.trunc_f64_s',
        Opcode.I64_TRUNC_F64_U: 'i64.trunc_f64_u',
        Opcode.F32_CONVERT_I32_S: 'f32.convert_i32_s',
        Opcode.F32_CONVERT_I32_U: 'f32.convert_i32_u',
        Opcode.F32_CONVERT_I64_S: 'f32.convert_i64_s',
        Opcode.F32_CONVERT_I64_U: 'f32.convert_i64_u',
        Opcode.F32_DEMOTE_F64: 'f32.demote_f64',
        Opcode.F64_CONVERT_I32_S: 'f64.convert_i32_s',
        Opcode.F64_CONVERT_I32_U: 'f64.convert_i32_u',
        Opcode.F64_CONVERT_I64_S: 'f64.convert_i64_s',
        Opcode.F64_CONVERT_I64_U: 'f64.convert_i64_u',
        Opcode.F64_PROMOTE_F32: 'f64.promote_f32',
        Opcode.I32_REINTERPRET_F32: 'i32.reinterpret_f32',
        Opcode.I64_REINTERPRET_F64: 'i64.reinterpret_f64',
        Opcode.F32_REINTERPRET_I32: 'f32.reinterpret_i32',
        Opcode.F64_REINTERPRET_I64: 'f64.reinterpret_i64',
        Opcode.REF_NULL: 'ref.null',
        Opcode.REF_IS_NULL: 'ref.is_null',
        Opcode.REF_FUNC: 'ref.func',
        Opcode.REF_AS_NON_NULL: 'ref.as_non_null',
        Opcode.BR_ON_NULL: 'br_on_null',
        Opcode.BR_ON_NON_NULL: 'br_on_non_null',
    }

    atomic_opcode_map = {
        AtomicOpcode.MEMORY_ATOMIC_NOTIFY: 'memory.atomic.notify',
        AtomicOpcode.MEMORY_ATOMIC_WAIT32: 'memory.atomic.wait32',
        AtomicOpcode.MEMORY_ATOMIC_WAIT64: 'memory.atomic.wait64',
        AtomicOpcode.ATOMIC_FENCE: 'atomic.fence',
        AtomicOpcode.I32_ATOMIC_LOAD: 'i32.atomic.load',
        AtomicOpcode.I64_ATOMIC_LOAD: 'i64.atomic.load',
        AtomicOpcode.I32_ATOMIC_LOAD8_U: 'i32.atomic.load8_u',
        AtomicOpcode.I32_ATOMIC_LOAD16_U: 'i32.atomic.load16_u',
        AtomicOpcode.I64_ATOMIC_LOAD8_U: 'i64.atomic.load8_u',
        AtomicOpcode.I64_ATOMIC_LOAD16_U: 'i64.atomic.load16_u',
        AtomicOpcode.I64_ATOMIC_LOAD32_U: 'i64.atomic.load32_u',
        AtomicOpcode.I32_ATOMIC_STORE: 'i32.atomic.store',
        AtomicOpcode.I64_ATOMIC_STORE: 'i64.atomic.store',
        AtomicOpcode.I32_ATOMIC_STORE8: 'i32.atomic.store8',
        AtomicOpcode.I32_ATOMIC_STORE16: 'i32.atomic.store16',
        AtomicOpcode.I64_ATOMIC_STORE8: 'i64.atomic.store8',
        AtomicOpcode.I64_ATOMIC_STORE16: 'i64.atomic.store16',
        AtomicOpcode.I64_ATOMIC_STORE32: 'i64.atomic.store32',
    }

    gc_opcode_map = {
        GCOpcode.STRUCT_NEW: 'struct.new',
        GCOpcode.STRUCT_NEW_DEFAULT: 'struct.new_default',
        GCOpcode.STRUCT_GET: 'struct.get',
        GCOpcode.STRUCT_GET_S: 'struct.get_s',
        GCOpcode.STRUCT_GET_U: 'struct.get_u',
        GCOpcode.STRUCT_SET: 'struct.set',
        GCOpcode.ARRAY_NEW: 'array.new',
        GCOpcode.ARRAY_NEW_DEFAULT: 'array.new_default',
        GCOpcode.ARRAY_NEW_FIXED: 'array.new_fixed',
        GCOpcode.ARRAY_NEW_DATA: 'array.new_data',
        GCOpcode.ARRAY_NEW_ELEM: 'array.new_elem',
        GCOpcode.ARRAY_GET: 'array.get',
        GCOpcode.ARRAY_GET_S: 'array.get_s',
        GCOpcode.ARRAY_GET_U: 'array.get_u',
        GCOpcode.ARRAY_SET: 'array.set',
        GCOpcode.ARRAY_LEN: 'array.len',
        GCOpcode.ARRAY_FILL: 'array.fill',
        GCOpcode.ARRAY_COPY: 'array.copy',
        GCOpcode.ARRAY_INIT_DATA: 'array.init_data',
        GCOpcode.ARRAY_INIT_ELEM: 'array.init_elem',
        GCOpcode.REF_TEST: 'ref.test',
        GCOpcode.REF_CAST: 'ref.cast',
        GCOpcode.BR_ON_CAST: 'br_on_cast',
        GCOpcode.BR_ON_CAST_FAIL: 'br_on_cast_fail',
        GCOpcode.ANY_CONVERT_EXTERN: 'any.convert_extern',
        GCOpcode.EXTERN_CONVERT_ANY: 'extern.convert_any',
        GCOpcode.REF_I31: 'ref.i31',
        GCOpcode.I31_GET_S: 'i31.get_s',
        GCOpcode.I31_GET_U: 'i31.get_u',
    }

    if isinstance(instr.opcode, Opcode):
        opcode_name = opcode_map.get(instr.opcode, str(instr.opcode))
    elif isinstance(instr.opcode, AtomicOpcode):
        opcode_name = atomic_opcode_map.get(instr.opcode, str(instr.opcode))
    elif isinstance(instr.opcode, GCOpcode):
        opcode_name = gc_opcode_map.get(instr.opcode, str(instr.opcode))
    else:
        opcode_name = str(instr.opcode)

    result = opcode_name

    if isinstance(instr, ConstInstruction):
        result += f' {instr.value}'
    elif isinstance(instr, LocalInstruction):
        result += f' {instr.local_idx}'
    elif isinstance(instr, GlobalInstruction):
        result += f' {instr.global_idx}'
    elif isinstance(instr, CallInstruction):
        result += f' {instr.func_idx}'
    elif isinstance(instr, CallIndirectInstruction):
        result += f' {instr.type_idx}'
        if instr.table_idx != 0:
            result += f' {instr.table_idx}'
    elif isinstance(instr, ReturnCallInstruction):
        result += f' {instr.func_idx}'
    elif isinstance(instr, ReturnCallIndirectInstruction):
        result += f' {instr.type_idx}'
        if instr.table_idx != 0:
            result += f' {instr.table_idx}'
    elif isinstance(instr, BrInstruction):
        result += f' {instr.label_idx}'
    elif isinstance(instr, BrTableInstruction):
        indices = ' '.join(str(idx) for idx in instr.label_indices)
        result += f' {indices} {instr.default_label}'
    elif isinstance(instr, BlockInstruction):
        block_type = ''
        if instr.block_type is not None:
            if isinstance(instr.block_type, ValType):
                block_type = f' (result {format_valtype(instr.block_type)})'
            else:
                block_type = f' (type {instr.block_type})'

        body = '\n'.join(format_instruction(i, indent_level + 1) for i in instr.instructions)
        result = f'{opcode_name}{block_type}\n{indent(body, indent_level + 1)}\nend'
    elif isinstance(instr, IfInstruction):
        block_type = ''
        if instr.block_type is not None:
            if isinstance(instr.block_type, ValType):
                block_type = f' (result {format_valtype(instr.block_type)})'
            else:
                block_type = f' (type {instr.block_type})'

        then_body = '\n'.join(
            format_instruction(i, indent_level + 1) for i in instr.then_instructions
        )
        result = f'{opcode_name}{block_type}\n{indent(then_body, indent_level + 1)}'

        if instr.else_instructions:
            else_body = '\n'.join(
                format_instruction(i, indent_level + 1) for i in instr.else_instructions
            )
            result += f'\nelse\n{indent(else_body, indent_level + 1)}'

        result += '\nend'
    elif isinstance(instr, MemoryInstruction):
        if instr.offset != 0:
            result += f' offset={instr.offset}'
        if instr.align != 0:
            result += f' align={1 << instr.align}'
    elif isinstance(instr, AtomicMemoryInstruction):
        if instr.offset != 0:
            result += f' offset={instr.offset}'
        if instr.align != 0:
            result += f' align={1 << instr.align}'
    elif isinstance(instr, RefNullInstruction):
        result += f' {format_reftype(instr.ref_type)}'
    elif isinstance(instr, RefFuncInstruction):
        result += f' {instr.func_idx}'
    elif isinstance(instr, StructNewInstruction):
        result += f' {instr.type_idx}'
    elif isinstance(instr, StructGetInstruction):
        result += f' {instr.type_idx} {instr.field_idx}'
    elif isinstance(instr, StructSetInstruction):
        result += f' {instr.type_idx} {instr.field_idx}'
    elif isinstance(instr, ArrayNewInstruction):
        result += f' {instr.type_idx}'
    elif isinstance(instr, ArrayGetInstruction):
        result += f' {instr.type_idx}'
    elif isinstance(instr, ArraySetInstruction):
        result += f' {instr.type_idx}'
    elif isinstance(instr, ArrayNewFixedInstruction):
        result += f' {instr.type_idx} {instr.size}'
    elif isinstance(instr, RefTestInstruction):
        result += f' {format_reftype(instr.ref_type)}'
    elif isinstance(instr, RefCastInstruction):
        result += f' {format_reftype(instr.ref_type)}'
    elif isinstance(instr, BrOnCastInstruction):
        result += f' {instr.label_idx} {format_reftype(instr.ref_type_from)} {format_reftype(instr.ref_type_to)}'

    return result


def format_expr(instructions: list[Instruction]) -> str:
    return '\n'.join(format_instruction(instr) for instr in instructions)


def format_section(section: Section) -> str:
    result = ''

    if isinstance(section, TypeSection):
        result += '(type\n'
        for i, typ in enumerate(section.types):
            if isinstance(typ, FuncType):
                result += f'  {format_functype(typ)}\n'
            elif isinstance(typ, StructType):
                result += f'  {format_structtype(typ)}\n'
            elif isinstance(typ, ArrayType):
                result += f'  {format_arraytype(typ)}\n'
        result += ')\n'

    elif isinstance(section, ImportSection):
        for imp in section.imports:
            if isinstance(imp.desc, FuncImportDesc):
                result += (
                    f'(import "{imp.module}" "{imp.name}" (func (type {imp.desc.type_idx})))\n'
                )
            elif isinstance(imp.desc, TableImportDesc):
                result += f'(import "{imp.module}" "{imp.name}" (table {format_tabletype(imp.desc.table_type)}))\n'
            elif isinstance(imp.desc, MemImportDesc):
                result += f'(import "{imp.module}" "{imp.name}" (memory {format_memtype(imp.desc.mem_type)}))\n'
            elif isinstance(imp.desc, GlobalImportDesc):
                result += f'(import "{imp.module}" "{imp.name}" (global {format_globaltype(imp.desc.global_type)}))\n'

    elif isinstance(section, FunctionSection):
        for i, type_idx in enumerate(section.type_indices):
            result += f'(func (type {type_idx}))\n'

    elif isinstance(section, TableSection):
        for table in section.tables:
            result += f'(table {format_tabletype(table.table_type)})\n'

    elif isinstance(section, MemorySection):
        for memory in section.memories:
            result += f'(memory {format_memtype(memory.mem_type)})\n'

    elif isinstance(section, GlobalSection):
        for glob in section.globals:
            init_expr = indent(format_expr(glob.init_expr))
            result += f'(global {format_globaltype(glob.global_type)}\n{init_expr}\n)\n'

    elif isinstance(section, ExportSection):
        for exp in section.exports:
            if isinstance(exp.desc, FuncExportDesc):
                result += f'(export "{exp.name}" (func {exp.desc.func_idx}))\n'
            elif isinstance(exp.desc, TableExportDesc):
                result += f'(export "{exp.name}" (table {exp.desc.table_idx}))\n'
            elif isinstance(exp.desc, MemExportDesc):
                result += f'(export "{exp.name}" (memory {exp.desc.mem_idx}))\n'
            elif isinstance(exp.desc, GlobalExportDesc):
                result += f'(export "{exp.name}" (global {exp.desc.global_idx}))\n'

    elif isinstance(section, StartSection):
        result += f'(start {section.func_idx})\n'

    elif isinstance(section, CodeSection):
        for i, func in enumerate(section.funcs):
            locals_decl = ''
            if func.locals:
                locals_parts = []
                for local in func.locals:
                    locals_parts.append(
                        f'(local {" ".join([format_valtype(local.val_type)] * local.count)})'
                    )
                locals_decl = ' ' + ' '.join(locals_parts)

            body = indent(format_expr(func.body))
            result += f'(func{locals_decl}\n{body}\n)\n'

    return result


def encode_text(module: Module) -> str:
    result = '(module\n'

    for section in module.sections:
        section_text = format_section(section)
        if section_text.strip():
            result += indent(section_text) + '\n'

    result += ')'
    return result
