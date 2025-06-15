from dataclasses import dataclass, field
from .sections import Section, GlobalSection, Global, ExportSection, Export, GlobalExportDesc
from .types import GlobalType, ValType
from .instructions import Instruction


@dataclass
class Module:
    version: int = 1
    sections: list[Section] = field(default_factory=list)

    def add_section(self, section: Section):
        self.sections.append(section)

    def add_global(
        self,
        modifier: str,
        value_type: str,
        initializer: list,
        export_as: str | None = None,
    ) -> int:
        """Add a global variable to the module.

        Args:
            modifier: 'const' or 'var'
            value_type: WASM value type ('i32', 'i64', 'f32', 'f64')
            initializer: List of instructions for the global's initial value
            export_as: Optional export name for the global

        Returns:
            Global index
        """
        # Validate modifier
        if modifier not in ['const', 'var']:
            raise TypeError(f'Expected modifier in ["const", "var"]. Received: {modifier!r}.')

        # Convert string value type to ValType enum
        value_type_map = {
            'i32': ValType.I32,
            'i64': ValType.I64,
            'f32': ValType.F32,
            'f64': ValType.F64,
            'funcref': ValType.FUNCREF,
            'externref': ValType.EXTERNREF,
        }

        if value_type not in value_type_map:
            raise TypeError(
                f'Expected value_type in {list(value_type_map.keys())}. Received: {value_type!r}.'
            )

        val_type = value_type_map[value_type]
        mutable = modifier == 'var'
        global_type = GlobalType(val_type=val_type, mutable=mutable)

        # Convert initializer to instructions if needed
        if not isinstance(initializer, list):
            initializer = [initializer]

        init_instructions = []
        for inst in initializer:
            if isinstance(inst, Instruction):
                init_instructions.append(inst)
            else:
                # For now, assume it's already a proper instruction representation
                init_instructions.append(inst)

        global_obj = Global(global_type=global_type, init_expr=init_instructions)

        # Find or create GlobalSection
        global_section = None
        for section in self.sections:
            if isinstance(section, GlobalSection):
                global_section = section
                break

        if global_section is None:
            global_section = GlobalSection(globals=[])
            self.add_section(global_section)

        global_index = len(global_section.globals)
        global_section.globals.append(global_obj)

        # Handle export if requested
        if export_as is not None:
            self._export_global(export_as, global_index)

        return global_index

    def _export_global(self, name: str, global_index: int):
        """Add a global export to the module."""
        export_desc = GlobalExportDesc(global_idx=global_index)
        export_obj = Export(name=name, desc=export_desc)

        # Find or create ExportSection
        export_section = None
        for section in self.sections:
            if isinstance(section, ExportSection):
                export_section = section
                break

        if export_section is None:
            export_section = ExportSection(exports=[])
            self.add_section(export_section)

        export_section.exports.append(export_obj)
