import json
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Symbol(BaseModel):
    """Unified symbol record representing any declared identifier (variable, constant, enum, interface, type)."""
    __tablename__ = "symbols"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True, default="proj_default")
    source_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False, index=True, default="file_default")
    
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="symbol")  # function, class, method, variable, constant, interface, type, module
    qualified_name: Mapped[str] = mapped_column(String(256), nullable=False, index=True, default="")
    visibility: Mapped[str] = mapped_column(String(16), default="public", nullable=False)
    
    start_line: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    start_col: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    end_col: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    docstring: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_exported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    source_file: Mapped["SourceFile"] = relationship("SourceFile", back_populates="symbols")

    def __init__(self, **kwargs):
        if "qualified_name" not in kwargs and "name" in kwargs:
            kwargs["qualified_name"] = kwargs["name"]
        super().__init__(**kwargs)


class FunctionDefinition(BaseModel):
    """Detailed record of a standalone function, class method, or arrow function definition."""
    __tablename__ = "function_definitions"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True, default="proj_default")
    source_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False, index=True, default="file_default")
    class_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("class_definitions.id", ondelete="CASCADE"), nullable=True)

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    qualified_name: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    start_line: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    line_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Signature & Arguments
    parameters_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    return_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    decorators_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    
    # Characteristics
    is_async: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_static: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_method: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_exported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    visibility: Mapped[str] = mapped_column(String(16), default="public", nullable=False)
    
    # Metrics
    cyclomatic_complexity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    cognitive_complexity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parameter_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    return_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    docstring: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    calls_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)

    source_file: Mapped["SourceFile"] = relationship("SourceFile", back_populates="functions")
    parent_class: Mapped[Optional["ClassDefinition"]] = relationship("ClassDefinition", back_populates="methods")

    def __init__(self, **kwargs):
        if "qualified_name" not in kwargs and "name" in kwargs:
            kwargs["qualified_name"] = kwargs["name"]
        if "parameters" in kwargs:
            val = kwargs.pop("parameters")
            kwargs["parameters_json"] = json.dumps(val) if not isinstance(val, str) else val
            kwargs["parameter_count"] = len(val) if isinstance(val, list) else 0
        if "decorators" in kwargs:
            val = kwargs.pop("decorators")
            kwargs["decorators_json"] = json.dumps(val) if not isinstance(val, str) else val
        if "calls" in kwargs:
            val = kwargs.pop("calls")
            kwargs["calls_json"] = json.dumps(val) if not isinstance(val, str) else val
        if "end_line" in kwargs and "start_line" in kwargs and "line_count" not in kwargs:
            kwargs["line_count"] = max(1, kwargs["end_line"] - kwargs["start_line"] + 1)
        super().__init__(**kwargs)

    @property
    def parameters(self) -> List[Any]:
        try:
            return json.loads(self.parameters_json)
        except Exception:
            return []

    @property
    def decorators(self) -> List[str]:
        try:
            return json.loads(self.decorators_json)
        except Exception:
            return []

    @property
    def calls(self) -> List[str]:
        try:
            return json.loads(self.calls_json)
        except Exception:
            return []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["parameters"] = self.parameters
        data["decorators"] = self.decorators
        data["calls"] = self.calls
        return data


class ClassDefinition(BaseModel):
    """Detailed record of a class, struct, interface, or trait definition."""
    __tablename__ = "class_definitions"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True, default="proj_default")
    source_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False, index=True, default="file_default")

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    qualified_name: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    start_line: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    line_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Hierarchy & Interfaces
    base_classes_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    interfaces_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    decorators_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    
    # Characteristics
    is_abstract: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_exported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    visibility: Mapped[str] = mapped_column(String(16), default="public", nullable=False)
    methods_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fields_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    docstring: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source_file: Mapped["SourceFile"] = relationship("SourceFile", back_populates="classes")
    methods: Mapped[List["FunctionDefinition"]] = relationship("FunctionDefinition", back_populates="parent_class", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if "qualified_name" not in kwargs and "name" in kwargs:
            kwargs["qualified_name"] = kwargs["name"]
        if "base_classes" in kwargs:
            val = kwargs.pop("base_classes")
            kwargs["base_classes_json"] = json.dumps(val) if not isinstance(val, str) else val
        if "interfaces" in kwargs:
            val = kwargs.pop("interfaces")
            kwargs["interfaces_json"] = json.dumps(val) if not isinstance(val, str) else val
        if "decorators" in kwargs:
            val = kwargs.pop("decorators")
            kwargs["decorators_json"] = json.dumps(val) if not isinstance(val, str) else val
        super().__init__(**kwargs)

    @property
    def base_classes(self) -> List[str]:
        try:
            return json.loads(self.base_classes_json)
        except Exception:
            return []

    @property
    def interfaces(self) -> List[str]:
        try:
            return json.loads(self.interfaces_json)
        except Exception:
            return []

    @property
    def decorators(self) -> List[str]:
        try:
            return json.loads(self.decorators_json)
        except Exception:
            return []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["base_classes"] = self.base_classes
        data["interfaces"] = self.interfaces
        data["decorators"] = self.decorators
        return data


class ImportStatement(BaseModel):
    """Normalized import/require statement linking source files to internal or external modules."""
    __tablename__ = "import_statements"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True, default="proj_default")
    source_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False, index=True, default="file_default")

    module_name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    imported_symbols_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    alias: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    is_relative: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_external: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_type_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    source_file: Mapped["SourceFile"] = relationship("SourceFile", back_populates="imports")

    def __init__(self, **kwargs):
        if "imported_symbols" in kwargs:
            val = kwargs.pop("imported_symbols")
            kwargs["imported_symbols_json"] = json.dumps(val) if not isinstance(val, str) else val
        if "imported_names" in kwargs:
            val = kwargs.pop("imported_names")
            kwargs["imported_symbols_json"] = json.dumps(val) if not isinstance(val, str) else val
        super().__init__(**kwargs)

    @property
    def imported_symbols(self) -> List[str]:
        try:
            return json.loads(self.imported_symbols_json)
        except Exception:
            return []

    @property
    def imported_names(self) -> List[str]:
        return self.imported_symbols

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["imported_symbols"] = self.imported_symbols
        data["imported_names"] = self.imported_symbols
        return data
