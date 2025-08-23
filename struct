from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Dict


class MagiDDL:

    def __init__(self):
        # necessary
        self.table: MagiTable or None = None
        # database specific
        self.schema_name: str or None = None
        self.tablespace: str or None = None
        self.storage_engine: str or None = None
        self.charset: str or None = None
        self.collation: str or None = None
        # options
        self.if_not_exists: bool = False
        self.temporary: bool = False
        self.options: Dict[str, str] = {}

    def get_ddl_string(self) -> str:
        if not self.table:
            return ''

        ddl_parts = ['CREATE']
        if self.temporary:
            ddl_parts.append('TEMPORARY')
        ddl_parts.append('TABLE')
        if self.if_not_exists:
            ddl_parts.append('IF NOT EXISTS')

        table_name = self.table.table_name
        if self.schema_name:
            table_name = f"{self.schema_name}.{table_name}"
        ddl_parts.append(table_name)

        return ' '.join(ddl_parts)


@dataclass
class MagiTableColumn:
    name: str
    data_type: str
    length: int or None = None
    precision: int or None = None
    primary_key: bool = False
    unique: bool = False
    not_null: bool = False
    default: str or None = None
    comment: str or None = None
    no: int or None = None
    
    def __str__(self):
        return f"name={self.name}, data_type={self.data_type}, length={self.length}, precision={self.precision}, primary_key={self.primary_key}, unique={self.unique}, not_null={self.not_null}, default={self.default}, comment={self.comment}, no={self.no}"


@dataclass
class MagiTableIndex:
    name: str
    columns: list[str] = field(default_factory=list)
    unique: bool = False


@dataclass
class MagiTable:
    table_name: str
    table_comment: str or None = None
    table_schema: str or None = None
    columns: Dict[str, MagiTableColumn] = field(default_factory=dict)
    indexes: Dict[str, MagiTableIndex] = field(default_factory=dict)

    def __str__(self):
        output = []
        output.append(f"table_name={self.table_name}")
        output.append(f"table_comment={self.table_comment}")
        output.append(f"table_schema={self.table_schema}")
        output.append("columns:")
        for col in self.columns.values():
            output.append(f"  {col}")
        output.append("indexes:")
        for idx in self.indexes.values():
            output.append(f"  {idx}")
        return '\n'.join(output)
