from dataclasses import dataclass, field
from .sections import Section


@dataclass
class Module:
    version: int = 1
    sections: list[Section] = field(default_factory=list)

    def add_section(self, section: Section):
        self.sections.append(section)
