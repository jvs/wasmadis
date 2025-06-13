from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum
from .types import ValType, RefType

class Opcode(Enum):
    UNREACHABLE = 0x00
    NOP = 0x01
    BLOCK = 0x02
    LOOP = 0x03
    IF = 0x04
    ELSE = 0x05
    END = 0x0B
    BR = 0x0C
    BR_IF = 0x0D
    BR_TABLE = 0x0E
    RETURN = 0x0F
    CALL = 0x10
    CALL_INDIRECT = 0x11
    RETURN_CALL = 0x12
    RETURN_CALL_INDIRECT = 0x13
    DROP = 0x1A
    SELECT = 0x1B
    SELECT_T = 0x1C
    LOCAL_GET = 0x20
    LOCAL_SET = 0x21
    LOCAL_TEE = 0x22
    GLOBAL_GET = 0x23
    GLOBAL_SET = 0x24
    TABLE_GET = 0x25
    TABLE_SET = 0x26
    I32_LOAD = 0x28
    I64_LOAD = 0x29
    F32_LOAD = 0x2A
    F64_LOAD = 0x2B
    I32_LOAD8_S = 0x2C
    I32_LOAD8_U = 0x2D
    I32_LOAD16_S = 0x2E
    I32_LOAD16_U = 0x2F
    I64_LOAD8_S = 0x30
    I64_LOAD8_U = 0x31
    I64_LOAD16_S = 0x32
    I64_LOAD16_U = 0x33
    I64_LOAD32_S = 0x34
    I64_LOAD32_U = 0x35
    I32_STORE = 0x36
    I64_STORE = 0x37
    F32_STORE = 0x38
    F64_STORE = 0x39
    I32_STORE8 = 0x3A
    I32_STORE16 = 0x3B
    I64_STORE8 = 0x3C
    I64_STORE16 = 0x3D
    I64_STORE32 = 0x3E
    MEMORY_SIZE = 0x3F
    MEMORY_GROW = 0x40
    I32_CONST = 0x41
    I64_CONST = 0x42
    F32_CONST = 0x43
    F64_CONST = 0x44
    I32_EQZ = 0x45
    I32_EQ = 0x46
    I32_NE = 0x47
    I32_LT_S = 0x48
    I32_LT_U = 0x49
    I32_GT_S = 0x4A
    I32_GT_U = 0x4B
    I32_LE_S = 0x4C
    I32_LE_U = 0x4D
    I32_GE_S = 0x4E
    I32_GE_U = 0x4F
    I64_EQZ = 0x50
    I32_ADD = 0x6A
    I32_SUB = 0x6B
    I32_MUL = 0x6C
    REF_NULL = 0xD0
    REF_IS_NULL = 0xD1
    REF_FUNC = 0xD2
    REF_AS_NON_NULL = 0xD3
    BR_ON_NULL = 0xD4
    BR_ON_NON_NULL = 0xD5

class AtomicOpcode(Enum):
    MEMORY_ATOMIC_NOTIFY = 0xFE00
    MEMORY_ATOMIC_WAIT32 = 0xFE01
    MEMORY_ATOMIC_WAIT64 = 0xFE02
    ATOMIC_FENCE = 0xFE03
    I32_ATOMIC_LOAD = 0xFE10
    I64_ATOMIC_LOAD = 0xFE11
    I32_ATOMIC_LOAD8_U = 0xFE12
    I32_ATOMIC_LOAD16_U = 0xFE13
    I64_ATOMIC_LOAD8_U = 0xFE14
    I64_ATOMIC_LOAD16_U = 0xFE15
    I64_ATOMIC_LOAD32_U = 0xFE16
    I32_ATOMIC_STORE = 0xFE17
    I64_ATOMIC_STORE = 0xFE18
    I32_ATOMIC_STORE8 = 0xFE19
    I32_ATOMIC_STORE16 = 0xFE1A
    I64_ATOMIC_STORE8 = 0xFE1B
    I64_ATOMIC_STORE16 = 0xFE1C
    I64_ATOMIC_STORE32 = 0xFE1D
    I32_ATOMIC_RMW_ADD = 0xFE1E
    I64_ATOMIC_RMW_ADD = 0xFE1F
    I32_ATOMIC_RMW8_ADD_U = 0xFE20
    I32_ATOMIC_RMW16_ADD_U = 0xFE21
    I64_ATOMIC_RMW8_ADD_U = 0xFE22
    I64_ATOMIC_RMW16_ADD_U = 0xFE23
    I64_ATOMIC_RMW32_ADD_U = 0xFE24
    I32_ATOMIC_RMW_SUB = 0xFE25
    I64_ATOMIC_RMW_SUB = 0xFE26
    I32_ATOMIC_RMW8_SUB_U = 0xFE27
    I32_ATOMIC_RMW16_SUB_U = 0xFE28
    I64_ATOMIC_RMW8_SUB_U = 0xFE29
    I64_ATOMIC_RMW16_SUB_U = 0xFE2A
    I64_ATOMIC_RMW32_SUB_U = 0xFE2B
    I32_ATOMIC_RMW_AND = 0xFE2C
    I64_ATOMIC_RMW_AND = 0xFE2D
    I32_ATOMIC_RMW8_AND_U = 0xFE2E
    I32_ATOMIC_RMW16_AND_U = 0xFE2F
    I64_ATOMIC_RMW8_AND_U = 0xFE30
    I64_ATOMIC_RMW16_AND_U = 0xFE31
    I64_ATOMIC_RMW32_AND_U = 0xFE32
    I32_ATOMIC_RMW_OR = 0xFE33
    I64_ATOMIC_RMW_OR = 0xFE34
    I32_ATOMIC_RMW8_OR_U = 0xFE35
    I32_ATOMIC_RMW16_OR_U = 0xFE36
    I64_ATOMIC_RMW8_OR_U = 0xFE37
    I64_ATOMIC_RMW16_OR_U = 0xFE38
    I64_ATOMIC_RMW32_OR_U = 0xFE39
    I32_ATOMIC_RMW_XOR = 0xFE3A
    I64_ATOMIC_RMW_XOR = 0xFE3B
    I32_ATOMIC_RMW8_XOR_U = 0xFE3C
    I32_ATOMIC_RMW16_XOR_U = 0xFE3D
    I64_ATOMIC_RMW8_XOR_U = 0xFE3E
    I64_ATOMIC_RMW16_XOR_U = 0xFE3F
    I64_ATOMIC_RMW32_XOR_U = 0xFE40
    I32_ATOMIC_RMW_XCHG = 0xFE41
    I64_ATOMIC_RMW_XCHG = 0xFE42
    I32_ATOMIC_RMW8_XCHG_U = 0xFE43
    I32_ATOMIC_RMW16_XCHG_U = 0xFE44
    I64_ATOMIC_RMW8_XCHG_U = 0xFE45
    I64_ATOMIC_RMW16_XCHG_U = 0xFE46
    I64_ATOMIC_RMW32_XCHG_U = 0xFE47
    I32_ATOMIC_RMW_CMPXCHG = 0xFE48
    I64_ATOMIC_RMW_CMPXCHG = 0xFE49
    I32_ATOMIC_RMW8_CMPXCHG_U = 0xFE4A
    I32_ATOMIC_RMW16_CMPXCHG_U = 0xFE4B
    I64_ATOMIC_RMW8_CMPXCHG_U = 0xFE4C
    I64_ATOMIC_RMW16_CMPXCHG_U = 0xFE4D
    I64_ATOMIC_RMW32_CMPXCHG_U = 0xFE4E

class GCOpcode(Enum):
    STRUCT_NEW = 0xFB00
    STRUCT_NEW_DEFAULT = 0xFB01
    STRUCT_GET = 0xFB02
    STRUCT_GET_S = 0xFB03
    STRUCT_GET_U = 0xFB04
    STRUCT_SET = 0xFB05
    ARRAY_NEW = 0xFB06
    ARRAY_NEW_DEFAULT = 0xFB07
    ARRAY_NEW_FIXED = 0xFB08
    ARRAY_NEW_DATA = 0xFB09
    ARRAY_NEW_ELEM = 0xFB0A
    ARRAY_GET = 0xFB0B
    ARRAY_GET_S = 0xFB0C
    ARRAY_GET_U = 0xFB0D
    ARRAY_SET = 0xFB0E
    ARRAY_LEN = 0xFB0F
    ARRAY_FILL = 0xFB10
    ARRAY_COPY = 0xFB11
    ARRAY_INIT_DATA = 0xFB12
    ARRAY_INIT_ELEM = 0xFB13
    REF_TEST = 0xFB14
    REF_CAST = 0xFB15
    BR_ON_CAST = 0xFB16
    BR_ON_CAST_FAIL = 0xFB17
    ANY_CONVERT_EXTERN = 0xFB18
    EXTERN_CONVERT_ANY = 0xFB19
    REF_I31 = 0xFB1A
    I31_GET_S = 0xFB1B
    I31_GET_U = 0xFB1C

@dataclass
class Instruction:
    opcode: Union[Opcode, AtomicOpcode, GCOpcode]
    
@dataclass
class ConstInstruction(Instruction):
    value: Union[int, float]

@dataclass
class LocalInstruction(Instruction):
    local_idx: int

@dataclass
class GlobalInstruction(Instruction):
    global_idx: int

@dataclass
class CallInstruction(Instruction):
    func_idx: int

@dataclass
class CallIndirectInstruction(Instruction):
    type_idx: int
    table_idx: int = 0

@dataclass
class ReturnCallInstruction(Instruction):
    func_idx: int

@dataclass
class ReturnCallIndirectInstruction(Instruction):
    type_idx: int
    table_idx: int = 0

@dataclass
class BrInstruction(Instruction):
    label_idx: int

@dataclass
class BrTableInstruction(Instruction):
    label_indices: List[int]
    default_label: int

@dataclass
class BlockInstruction(Instruction):
    block_type: Union[ValType, int, None]
    instructions: List[Instruction]

@dataclass
class IfInstruction(Instruction):
    block_type: Union[ValType, int, None]
    then_instructions: List[Instruction]
    else_instructions: Optional[List[Instruction]] = None

@dataclass
class MemoryInstruction(Instruction):
    align: int
    offset: int
    memory_idx: int = 0

@dataclass
class AtomicMemoryInstruction(Instruction):
    align: int
    offset: int
    memory_idx: int = 0

@dataclass
class RefNullInstruction(Instruction):
    ref_type: RefType

@dataclass
class RefFuncInstruction(Instruction):
    func_idx: int

@dataclass
class StructNewInstruction(Instruction):
    type_idx: int

@dataclass
class StructGetInstruction(Instruction):
    type_idx: int
    field_idx: int

@dataclass
class StructSetInstruction(Instruction):
    type_idx: int
    field_idx: int

@dataclass
class ArrayNewInstruction(Instruction):
    type_idx: int

@dataclass
class ArrayGetInstruction(Instruction):
    type_idx: int

@dataclass
class ArraySetInstruction(Instruction):
    type_idx: int

@dataclass
class ArrayNewFixedInstruction(Instruction):
    type_idx: int
    size: int

@dataclass
class RefTestInstruction(Instruction):
    ref_type: RefType

@dataclass
class RefCastInstruction(Instruction):
    ref_type: RefType

@dataclass
class BrOnCastInstruction(Instruction):
    label_idx: int
    ref_type_from: RefType
    ref_type_to: RefType