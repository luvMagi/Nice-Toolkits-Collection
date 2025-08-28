from dataclasses import dataclass
from src.magilib.database.model.structure import MagiTable, MagiTableColumn
from typing import List, Optional
import pandas as pd
from enum import Enum


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
    # 新增生成值列
    generated_value: str = 'generated_value'


class LengthRatio(Enum):
    """位数比例枚举"""
    ONE_THIRD = 1/3      # 三分之一
    HALF = 1/2           # 二分之一
    FULL = 1             # 最大位数


class TextFillMode(Enum):
    """文字填充模式"""
    ONLY_N = "only_n"           # 只用N填充
    COMMENT_PLUS_N = "comment_n" # comment + N填充


class TestDataGenerator:
    """生成测试数据的INSERT语句"""
    
    ORACLE_MAX_DATE = "DATE '9999-12-31'"
    
    def __init__(self, length_ratio: LengthRatio = LengthRatio.FULL, 
                 text_fill_mode: TextFillMode = TextFillMode.ONLY_N):
        self.data_frame: Optional[pd.DataFrame] = None
        self.length_ratio = length_ratio
        self.text_fill_mode = text_fill_mode
    
    def calculate_actual_length(self, max_length: int) -> int:
        """根据比例计算实际使用的长度"""
        if max_length <= 0:
            return 1
        actual_length = int(max_length * self.length_ratio.value)
        return max(1, actual_length)  # 至少为1
    
    def generate_text_value(self, column: MagiTableColumn) -> str:
        """生成文字类型的值"""
        max_length = column.length or 1
        actual_length = self.calculate_actual_length(max_length)
        
        if self.text_fill_mode == TextFillMode.COMMENT_PLUS_N:
            comment = column.comment or ""
            # 移除comment中的引号，避免SQL语法错误
            clean_comment = comment.replace("'", "").replace('"', '')
            
            if clean_comment:
                # 计算comment长度，剩余用N填充
                comment_length = len(clean_comment)
                if comment_length >= actual_length:
                    # 如果comment太长，截取到指定长度
                    result_text = clean_comment[:actual_length]
                else:
                    # comment + N填充到指定长度
                    n_count = actual_length - comment_length
                    result_text = clean_comment + 'N' * n_count
            else:
                # 没有comment，只用N填充
                result_text = 'N' * actual_length
        else:
            # 只用N填充
            result_text = 'N' * actual_length
        
        return f"'{result_text}'"
    
    def generate_number_value(self, column: MagiTableColumn) -> str:
        """生成数字类型的值"""
        max_length = column.length or 9
        actual_length = self.calculate_actual_length(max_length)
        return '9' * actual_length
    
    def generate_default_value(self, column: MagiTableColumn) -> str:
        """根据列的数据类型生成默认值"""
        data_type = column.data_type.upper()
        
        # 字符串类型
        if data_type in ['VARCHAR', 'VARCHAR2', 'CHAR', 'NVARCHAR', 'NCHAR', 'TEXT', 'CLOB']:
            return self.generate_text_value(column)
        
        # 数字类型
        elif data_type in ['INTEGER', 'INT', 'NUMBER', 'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE']:
            return self.generate_number_value(column)
        
        # 日期类型
        elif data_type in ['DATE', 'TIMESTAMP', 'DATETIME']:
            return self.ORACLE_MAX_DATE
        
        # 布尔类型
        elif data_type in ['BOOLEAN', 'BOOL']:
            return 'TRUE'
        
        # 默认情况
        else:
            return 'NULL'
    
    def generate_dataframe(self, table: MagiTable) -> pd.DataFrame:
        """生成包含表结构和测试值的DataFrame"""
        # 获取排序后的列
        sorted_columns = sorted(table.columns.values(), key=lambda x: x.no or 0)
        
        # 准备DataFrame数据
        data = {
            DefineDataFrameColumns.name: [],
            DefineDataFrameColumns.data_type: [],
            DefineDataFrameColumns.length: [],
            DefineDataFrameColumns.precision: [],
            DefineDataFrameColumns.primary_key: [],
            DefineDataFrameColumns.unique: [],
            DefineDataFrameColumns.not_null: [],
            DefineDataFrameColumns.default: [],
            DefineDataFrameColumns.comment: [],
            DefineDataFrameColumns.generated_value: []
        }
        
        # 填充数据
        for column in sorted_columns:
            data[DefineDataFrameColumns.name].append(column.name)
            data[DefineDataFrameColumns.data_type].append(column.data_type)
            data[DefineDataFrameColumns.length].append(column.length)
            data[DefineDataFrameColumns.precision].append(column.precision)
            data[DefineDataFrameColumns.primary_key].append(column.primary_key)
            data[DefineDataFrameColumns.unique].append(column.unique)
            data[DefineDataFrameColumns.not_null].append(column.not_null)
            data[DefineDataFrameColumns.default].append(column.default)
            data[DefineDataFrameColumns.comment].append(column.comment)
            
            # 生成测试值
            if column.default and column.default != 'NULL':
                generated_value = column.default
            else:
                generated_value = self.generate_default_value(column)
            data[DefineDataFrameColumns.generated_value].append(generated_value)
        
        self.data_frame = pd.DataFrame(data)
        return self.data_frame
    
    def set_length_ratio(self, ratio: LengthRatio):
        """设置长度比例"""
        self.length_ratio = ratio
        print(f"长度比例已设置为: {ratio.name} ({ratio.value})")
    
    def set_text_fill_mode(self, mode: TextFillMode):
        """设置文字填充模式"""
        self.text_fill_mode = mode
        print(f"文字填充模式已设置为: {mode.value}")
    
    def save_dataframe_to_csv(self, file_path: str) -> None:
        """保存DataFrame到CSV文件"""
        if self.data_frame is None:
            raise ValueError("DataFrame未生成，请先调用generate_dataframe方法")
        
        self.data_frame.to_csv(file_path, index=False, encoding='utf-8')
        print(f"DataFrame已保存到: {file_path}")
    
    def load_dataframe_from_csv(self, file_path: str) -> pd.DataFrame:
        """从CSV文件加载DataFrame"""
        self.data_frame = pd.read_csv(file_path, encoding='utf-8')
        return self.data_frame
    
    def generate_insert_from_dataframe(self, table_name: str, schema_name: Optional[str] = None, 
                                     rows_count: int = 1, output_csv: Optional[str] = None) -> List[str]:
        """基于DataFrame生成INSERT语句"""
        if self.data_frame is None:
            raise ValueError("DataFrame未加载，请先调用generate_dataframe或load_dataframe_from_csv方法")
        
        # 构建表名
        full_table_name = table_name
        if schema_name:
            full_table_name = f"{schema_name}.{table_name}"
        
        # 获取列名和生成的值
        column_names = self.data_frame[DefineDataFrameColumns.name].tolist()
        generated_values = self.data_frame[DefineDataFrameColumns.generated_value].tolist()
        
        # 生成INSERT语句
        insert_statements = []
        for row_index in range(rows_count):
            columns_str = ', '.join(column_names)
            values_str = ', '.join(generated_values)
            
            insert_sql = f"INSERT INTO {full_table_name} ({columns_str}) VALUES ({values_str});"
            insert_statements.append(insert_sql)
        
        # 可选输出到CSV
        if output_csv:
            insert_df = pd.DataFrame({'insert_statements': insert_statements})
            insert_df.to_csv(output_csv, index=False, encoding='utf-8')
            print(f"INSERT语句已保存到: {output_csv}")
        
        return insert_statements
    
    def generate_batch_insert_from_dataframe(self, table_name: str, schema_name: Optional[str] = None, 
                                           rows_count: int = 5, output_csv: Optional[str] = None) -> str:
        """基于DataFrame生成批量INSERT语句"""
        if self.data_frame is None:
            raise ValueError("DataFrame未加载，请先调用generate_dataframe或load_dataframe_from_csv方法")
        
        # 构建表名
        full_table_name = table_name
        if schema_name:
            full_table_name = f"{schema_name}.{table_name}"
        
        # 获取列名和生成的值
        column_names = self.data_frame[DefineDataFrameColumns.name].tolist()
        generated_values = self.data_frame[DefineDataFrameColumns.generated_value].tolist()
        
        columns_str = ', '.join(column_names)
        
        # 生成多行值
        values_list = []
        for row_index in range(rows_count):
            values_str = ', '.join(generated_values)
            values_list.append(f"({values_str})")
        
        batch_values_str = ',\n  '.join(values_list)
        
        batch_insert_sql = f"""INSERT INTO {full_table_name} ({columns_str}) 
VALUES 
  {batch_values_str};"""
        
        # 可选输出到CSV
        if output_csv:
            insert_df = pd.DataFrame({'batch_insert_statement': [batch_insert_sql]})
            insert_df.to_csv(output_csv, index=False, encoding='utf-8')
            print(f"批量INSERT语句已保存到: {output_csv}")
        
        return batch_insert_sql


from dataclasses import dataclass

from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd

from src.magilib.database.model.structure import MagiTable, MagiTableColumn, MagiTableIndex
from typing import List


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
            DefineDataFrameColumns.scale,
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
            iter_column.scale = row[DefineDataFrameColumns.scale]
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


 # Usage Example:
class DemoTableLConstructImpl(TableConstruct):

    def read_define(self):
        self.read_define_schema()
        self.read_define_columns()
        self.read_define_indexes()

    def read_define_schema(self):
        self.table_name = 'MagiOrigin'
        self.table_comment = 'Test Table'
        self.table_schema = 'luvmagi'

    def read_define_columns(self):
        self.columns_view = DefineDataFrameColumns.generate_csv_data()

    def read_define_indexes(self):
        ...


# 使用示例
if __name__ == "__main__":
    # 创建示例表
    table = MagiTable("test_table")
    table.table_schema = "test_schema"
    
    # 添加列
    table.columns["id"] = MagiTableColumn("id", "INTEGER", length=10, primary_key=True, not_null=True, no=1, comment="主键ID")
    table.columns["name"] = MagiTableColumn("name", "VARCHAR", length=50, not_null=True, no=2, comment="用户姓名")
    table.columns["email"] = MagiTableColumn("email", "VARCHAR", length=100, unique=True, no=3, comment="邮箱地址")
    table.columns["amount"] = MagiTableColumn("amount", "NUMBER", length=15, no=4, comment="金额")
    table.columns["created_date"] = MagiTableColumn("created_date", "DATE", default="SYSDATE", no=5, comment="创建日期")
    
    print("=== 测试不同的长度比例和填充模式 ===")
    
    # 测试1: 三分之一长度 + 只用N填充
    print("\n--- 三分之一长度 + 只用N填充 ---")
    generator1 = TestDataGenerator(LengthRatio.ONE_THIRD, TextFillMode.ONLY_N)
    df1 = generator1.generate_dataframe(table)
    print(df1[['name', 'data_type', 'length', 'comment', 'generated_value']])
    
    # 测试2: 二分之一长度 + comment+N填充
    print("\n--- 二分之一长度 + comment+N填充 ---")
    generator2 = TestDataGenerator(LengthRatio.HALF, TextFillMode.COMMENT_PLUS_N)
    df2 = generator2.generate_dataframe(table)
    print(df2[['name', 'data_type', 'length', 'comment', 'generated_value']])
    
    # 测试3: 最大长度 + comment+N填充
    print("\n--- 最大长度 + comment+N填充 ---")
    generator3 = TestDataGenerator(LengthRatio.FULL, TextFillMode.COMMENT_PLUS_N)
    df3 = generator3.generate_dataframe(table)
    print(df3[['name', 'data_type', 'length', 'comment', 'generated_value']])
    
    # 生成INSERT语句
    print("\n=== 生成的INSERT语句 (comment+N模式) ===")
    inserts = generator3.generate_insert_from_dataframe("test_table", "test_schema", 2)
    for insert_sql in inserts:
        print(insert_sql)
    
    # 动态改变设置
    print("\n=== 动态改变设置 ===")
    generator3.set_length_ratio(LengthRatio.ONE_THIRD)
    generator3.set_text_fill_mode(TextFillMode.ONLY_N)
    df4 = generator3.generate_dataframe(table)
    print(df4[['name', 'data_type', 'length', 'comment', 'generated_value']])
