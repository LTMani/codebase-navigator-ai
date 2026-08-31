import json
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Symbol(BaseModel):
    """Unified symbol record representing any declared identifier (variable, constant, enum, interface, type)."""
    __tablename__ = "symbols"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    source_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)  # function, class, method, variable, constant, interface, type, module
    qualified_name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    visibility: Mapped[str] = mapped_column(String(16), default="public", nullable=False)  # public, private, protected, internal
    
    start_line: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    start_col: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    end_col: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    docstring: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_exported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    source_file: Mapped["SourceFile"] = relationship("SourceFile", back_populates="symbols")


class FunctionDefinition(BaseModel):
    """Detailed record of a standalone function, class method, or arrow function definition."""
    __tablename__ = "function_definitions"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    source_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("class_definitions.id", ondelete="CASCADE"), nullable=True)

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    qualified_name: Mapped[str] = mapped_column(String(256), nullable=False)
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
    visibility: Mapped[str] = mapped_column(String(16), default="public", nullable=False)
    
    # Metrics
    cyclomatic_complexity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    cognitive_complexity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parameter_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    return_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    docstring: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    calls_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)  # Callee functions

    source_file: Mapped["SourceFile"] = relationship("SourceFile", back_populates="functions")
    parent_class: Mapped[Optional["ClassDefinition"]] = relationship("ClassDefinition", back_populates="methods")

    @property
    def parameters(self) -> List[Dict[str, Any]]:
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

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    source_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    qualified_name: Mapped[str] = mapped_column(String(256), nullable=False)
    start_line: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    line_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    base_classes_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    interfaces_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    decorators_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    methods_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fields_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    docstring: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source_file: Mapped["SourceFile"] = relationship("SourceFile", back_populates="classes")
    methods: Mapped[List["FunctionDefinition"]] = relationship("FunctionDefinition", back_populates="parent_class", cascade="all, delete-orphan")

    @property
    def base_classes(self) -> List[str]:
        try:
            return json.loads(self.base_classes_json)
        except Exception:
            return []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["base_classes"] = self.base_classes
        return data


class ImportStatement(BaseModel):
    """Records import statements and external module references per source file."""
    __tablename__ = "import_statements"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    source_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False, index=True)

    module_name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    imported_names_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    alias: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    line_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_relative: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_external: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    source_file: Mapped["SourceFile"] = relationship("SourceFile", back_populates="imports")
