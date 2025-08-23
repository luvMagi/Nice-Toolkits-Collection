from dataclasses import dataclass

from src.magilib.database.model.structure import MagiTable, MagiTableIndex, MagiTableColumn, MagiDDL
from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd


@dataclass(frozen=True)
class DefineDataFrameColumns:
    name: str = 'name'
    data_type: str = 'data_type'
    length: str = 'length'
    precision: str = 'precision'
    primary_key: str = 'primary_key'
    unique: str = 'unique'
    not_null: str = 'not_null'
    default: str = 'default'
    comment: str = 'comment'

    @classmethod
    def generate_csv_data(cls) -> pd.DataFrame:
        data = {
            cls.name: ['id', 'name', 'email', 'created_at', 'status'],
            cls.data_type: ['INTEGER', 'VARCHAR', 'VARCHAR', 'TIMESTAMP', 'CHAR'],
            cls.length: [None, 100, 255, None, 1],
            cls.precision: [None, None, None, None, None],
            cls.primary_key: [True, False, False, False, False],
            cls.unique: [False, False, True, False, False],
            cls.not_null: [True, True, True, True, True],
            cls.default: [None, None, None, 'CURRENT_TIMESTAMP', "'A'"],
            cls.comment: ['Primary key', 'User name', 'Email address', 'Creation timestamp', 'Record status']
        }
        return pd.DataFrame(data)

class TableConstruct(ABC):

    def __init__(self):
        self.table_name: str or None = None
        self.table_comment: str or None = None
        self.table_schema: str or None = None
        self.indexes: Dict[str, MagiTableIndex] = {}

        self.columns_view: pd.DataFrame = pd.DataFrame(columns=[
            DefineDataFrameColumns.name,
            DefineDataFrameColumns.data_type,
            DefineDataFrameColumns.length,
            DefineDataFrameColumns.precision,
            DefineDataFrameColumns.primary_key,
            DefineDataFrameColumns.unique,
            DefineDataFrameColumns.not_null,
            DefineDataFrameColumns.default,
            DefineDataFrameColumns.comment,
        ])

    # <editor-fold desc="Read From Excel Table Design Book, gather define to magi dedicated csv">
    @abstractmethod
    def read_define(self):
        self.read_define_schema()
        self.read_define_columns()
        self.read_define_indexes()

    @abstractmethod
    def read_define_schema(self): ...

    @abstractmethod
    def read_define_columns(self): ...

    @abstractmethod
    def read_define_indexes(self): ...

    # </editor-fold>

    def __extract_columns_to_magi_columns(self) -> Dict[str, MagiTableColumn]:
        dictionary: Dict[str, MagiTableColumn] = {}
        for index, (_, row) in enumerate(self.columns_view.iterrows()):
            iter_column = MagiTableColumn('', '')
            iter_column.name = row[DefineDataFrameColumns.name]
            iter_column.data_type = row[DefineDataFrameColumns.data_type]
            iter_column.length = row[DefineDataFrameColumns.length]
            iter_column.precision = row[DefineDataFrameColumns.precision]
            iter_column.primary_key = row[DefineDataFrameColumns.primary_key]
            iter_column.unique = row[DefineDataFrameColumns.unique]
            iter_column.not_null = row[DefineDataFrameColumns.not_null]
            iter_column.default = row[DefineDataFrameColumns.default]
            iter_column.comment = row[DefineDataFrameColumns.comment]
            iter_column.no = index + 1
            dictionary[iter_column.name] = iter_column
        return dictionary

    def magi_table_factory(self) -> MagiTable:
        self.read_define()
        object = MagiTable(self.table_name)
        object.table_comment = self.table_comment
        object.table_schema = self.table_schema
        object.columns = self.__extract_columns_to_magi_columns()
        object.indexes = self.indexes
        return object

#  Usage Example:
# class DemoTableLConstructImpl(TableConstruct):
#
#     def read_define(self):
#         self.read_define_schema()
#         self.read_define_columns()
#         self.read_define_indexes()
#
#     def read_define_schema(self):
#         self.table_name = 'MagiOrigin'
#         self.table_comment = 'Test Table'
#         self.table_schema = 'luvmagi'
#
#     def read_define_columns(self):
#         self.columns_view = DefineDataFrameColumns.generate_csv_data()
#
#     def read_define_indexes(self):
#         ...
#
#
# tester = DemoTableLConstructImpl()
# table = tester.magi_table_factory()
#
# ddl_construct = DDLConstruct()
#
# print(ddl_construct.create_table(table))