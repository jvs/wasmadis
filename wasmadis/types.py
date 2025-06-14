from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ValType(Enum):
    I32 = 0x7F
    I64 = 0x7E
    F32 = 0x7D
    F64 = 0x7C
    V128 = 0x7B
    FUNCREF = 0x70
    EXTERNREF = 0x6F
    ANYREF = 0x6E
    EQREF = 0x6D
    I31REF = 0x6C
    STRUCTREF = 0x6B
    ARRAYREF = 0x6A
    NULLFUNCREF = 0x73
    NULLEXTERNREF = 0x72
    NULLREF = 0x71


@dataclass
class RefType:
    nullable: bool
    heap_type: ValType | int


@dataclass
class FuncType:
    params: list[ValType]
    results: list[ValType]


@dataclass
class StructType:
    fields: list[FieldType]


@dataclass
class ArrayType:
    element_type: FieldType


@dataclass
class FieldType:
    storage_type: ValType | PackedType
    mutable: bool


class PackedType(Enum):
    I8 = 0x78
    I16 = 0x77


@dataclass
class Limits:
    min: int
    max: int | None = None
    shared: bool = False


@dataclass
class MemType:
    limits: Limits


@dataclass
class TableType:
    element_type: RefType
    limits: Limits


@dataclass
class GlobalType:
    val_type: ValType
    mutable: bool


CompositeType = FuncType | StructType | ArrayType
