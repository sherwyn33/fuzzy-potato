from typing import List


class SqlObjectDetail:
    def __int__(self, table_name: str, title: str, sql_type: str, options: List[str], variable_names: dict,
                variable_options: dict):
        self.table_name = table_name
        self.title = title
        self.sql_type = sql_type
        self.options = options
        self.variable_names = variable_names
        self.variable_options = variable_options

    def __new__(cls):
        obj = super().__new__(cls)
        obj.table_name = ""
        obj.title = ""
        obj.sql_type = ""
        obj.options = list()
        obj.variable_names = dict()
        obj.variable_options = dict()
        return obj
