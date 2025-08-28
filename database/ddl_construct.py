
from src.magilib.database.model.structure import MagiDDL, MagiTable, MagiTableColumn, MagiTableIndex


class DDLConstruct:
    SUPPORTED_DATABASES = ['oracle', 'postgres']

    def __init__(self):
        pass

    def _build_column_definition(self, column: 'MagiTableColumn', database: str) -> str:
        parts = [column.name, column.data_type]

        if column.length and column.data_type.lower() in ('varchar', 'char'):
            parts[1] = f"{parts[1]}({column.length})"

        if column.primary_key:
            parts.append('PRIMARY KEY')
        if column.not_null:
            parts.append('NOT NULL')
        if column.default is not None:
            parts.append(f"DEFAULT {column.default}")

        return ' '.join(parts)

    def _build_index_definition(self, table_name: str, index: 'MagiTableIndex') -> str:
        index_type = 'UNIQUE INDEX' if index.unique else 'INDEX'
        columns = ', '.join(index.columns)
        return f"CREATE {index_type} {index.name} ON {table_name} ({columns})"

    def create_table(self, magi_table: MagiTable, database='oracle') -> str:
        if database.lower() not in self.SUPPORTED_DATABASES:
            raise ValueError(f"Unsupported database: {database}. Supported databases: {self.SUPPORTED_DATABASES}")

        ddl = MagiDDL()
        ddl.table = magi_table

        # Build base CREATE TABLE statement
        ddl_str = ddl.get_ddl_string()

        # Add column definitions
        columns = [
            self._build_column_definition(col, database)
            for col in magi_table.columns.values()
        ]
        ddl_str += f" (\n    {',\n    '.join(columns)}\n)"

        # Add table comment if exists
        if magi_table.table_comment:
            if database == 'oracle':
                ddl_str += f"\nCOMMENT ON TABLE {magi_table.table_name} IS '{magi_table.table_comment}'"
            else:  # postgres
                ddl_str += f"\nCOMMENT ON TABLE {magi_table.table_name} IS '{magi_table.table_comment}'"

        # Add column comments if they exist
        for column in magi_table.columns.values():
            if column.comment:
                ddl_str += f";\nCOMMENT ON COLUMN {magi_table.table_name}.{column.name} IS '{column.comment}'"

        # Add indexes
        if magi_table.indexes:
            index_statements = [
                self._build_index_definition(magi_table.table_name, idx)
                for idx in magi_table.indexes.values()
            ]
            ddl_str += ';\n' + ';\n'.join(index_statements)

        return ddl_str
