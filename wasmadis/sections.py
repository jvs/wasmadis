from dataclasses import dataclass
from typing import List
from enum import Enum
from .types import *
from .instructions import Instruction


class SectionId(Enum):
    CUSTOM = 0
    TYPE = 1
    IMPORT = 2
    FUNCTION = 3
    TABLE = 4
    MEMORY = 5
    GLOBAL = 6
    EXPORT = 7
    START = 8
    ELEMENT = 9
    CODE = 10
    DATA = 11
    DATACOUNT = 12


@dataclass
class Section:
    pass


@dataclass
class CustomSection(Section):
    name: str
    data: bytes

    def __post_init__(self):
        self.id = SectionId.CUSTOM


@dataclass
class TypeSection(Section):
    types: List[CompositeType]

    def __post_init__(self):
        self.id = SectionId.TYPE


@dataclass
class ImportDesc:
    pass


@dataclass
class FuncImportDesc(ImportDesc):
    type_idx: int


@dataclass
class TableImportDesc(ImportDesc):
    table_type: TableType


@dataclass
class MemImportDesc(ImportDesc):
    mem_type: MemType


@dataclass
class GlobalImportDesc(ImportDesc):
    global_type: GlobalType


@dataclass
class Import:
    module: str
    name: str
    desc: ImportDesc


@dataclass
class ImportSection(Section):
    imports: List[Import]

    def __post_init__(self):
        self.id = SectionId.IMPORT


@dataclass
class FunctionSection(Section):
    type_indices: List[int]

    def __post_init__(self):
        self.id = SectionId.FUNCTION


@dataclass
class Table:
    table_type: TableType


@dataclass
class TableSection(Section):
    tables: List[Table]

    def __post_init__(self):
        self.id = SectionId.TABLE


@dataclass
class Memory:
    mem_type: MemType


@dataclass
class MemorySection(Section):
    memories: List[Memory]

    def __post_init__(self):
        self.id = SectionId.MEMORY


@dataclass
class Global:
    global_type: GlobalType
    init_expr: List[Instruction]


@dataclass
class GlobalSection(Section):
    globals: List[Global]

    def __post_init__(self):
        self.id = SectionId.GLOBAL


@dataclass
class ExportDesc:
    pass


@dataclass
class FuncExportDesc(ExportDesc):
    func_idx: int


@dataclass
class TableExportDesc(ExportDesc):
    table_idx: int


@dataclass
class MemExportDesc(ExportDesc):
    mem_idx: int


@dataclass
class GlobalExportDesc(ExportDesc):
    global_idx: int


@dataclass
class Export:
    name: str
    desc: ExportDesc


@dataclass
class ExportSection(Section):
    exports: List[Export]

    def __post_init__(self):
        self.id = SectionId.EXPORT


@dataclass
class StartSection(Section):
    func_idx: int

    def __post_init__(self):
        self.id = SectionId.START


@dataclass
class ElementMode:
    pass


@dataclass
class PassiveElementMode(ElementMode):
    pass


@dataclass
class ActiveElementMode(ElementMode):
    table_idx: int
    offset_expr: List[Instruction]


@dataclass
class DeclarativeElementMode(ElementMode):
    pass


@dataclass
class Element:
    ref_type: RefType
    init_exprs: List[List[Instruction]]
    mode: ElementMode


@dataclass
class ElementSection(Section):
    elements: List[Element]

    def __post_init__(self):
        self.id = SectionId.ELEMENT


@dataclass
class Locals:
    count: int
    val_type: ValType


@dataclass
class Func:
    locals: List[Locals]
    body: List[Instruction]


@dataclass
class CodeSection(Section):
    funcs: List[Func]

    def __post_init__(self):
        self.id = SectionId.CODE


@dataclass
class DataMode:
    pass


@dataclass
class PassiveDataMode(DataMode):
    pass


@dataclass
class ActiveDataMode(DataMode):
    mem_idx: int
    offset_expr: List[Instruction]


@dataclass
class Data:
    init: bytes
    mode: DataMode


@dataclass
class DataSection(Section):
    data: List[Data]

    def __post_init__(self):
        self.id = SectionId.DATA


@dataclass
class DataCountSection(Section):
    count: int

    def __post_init__(self):
        self.id = SectionId.DATACOUNT
