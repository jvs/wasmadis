from dataclasses import dataclass, field
from typing import List, Optional
from .sections import *

@dataclass
class Module:
    version: int = 1
    sections: List[Section] = field(default_factory=list)
    
    def add_section(self, section: Section):
        self.sections.append(section)
    
    def get_section(self, section_type: type) -> Optional[Section]:
        for section in self.sections:
            if isinstance(section, section_type):
                return section
        return None
    
    def get_sections(self, section_type: type) -> List[Section]:
        return [section for section in self.sections if isinstance(section, section_type)]
    
    def get_type_section(self) -> Optional[TypeSection]:
        return self.get_section(TypeSection)
    
    def get_import_section(self) -> Optional[ImportSection]:
        return self.get_section(ImportSection)
    
    def get_function_section(self) -> Optional[FunctionSection]:
        return self.get_section(FunctionSection)
    
    def get_table_section(self) -> Optional[TableSection]:
        return self.get_section(TableSection)
    
    def get_memory_section(self) -> Optional[MemorySection]:
        return self.get_section(MemorySection)
    
    def get_global_section(self) -> Optional[GlobalSection]:
        return self.get_section(GlobalSection)
    
    def get_export_section(self) -> Optional[ExportSection]:
        return self.get_section(ExportSection)
    
    def get_start_section(self) -> Optional[StartSection]:
        return self.get_section(StartSection)
    
    def get_element_section(self) -> Optional[ElementSection]:
        return self.get_section(ElementSection)
    
    def get_code_section(self) -> Optional[CodeSection]:
        return self.get_section(CodeSection)
    
    def get_data_section(self) -> Optional[DataSection]:
        return self.get_section(DataSection)
    
    def get_datacount_section(self) -> Optional[DataCountSection]:
        return self.get_section(DataCountSection)
    
    def get_custom_sections(self) -> List[CustomSection]:
        return self.get_sections(CustomSection)