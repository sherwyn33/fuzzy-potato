from typing import List

from Angular.typescript_helper_functions import get_ts_type
from sql_object_detail import SqlObjectDetail
from global_helper_functions import first_lowercase, combine_sql_list


def create_ts_object(sql_object_list: List[SqlObjectDetail]) -> str:
    sql_obj = combine_sql_list(sql_object_list)
    includeQuery = len(
        {key: sql_obj.options[key] for key in sql_obj.options if "filterTable" in sql_obj.options[key]}) > 0
    string = """export interface """ + sql_obj.title + "\n {\n"
    for key in sql_obj.variable_names:
        if sql_obj.variable_options[key] is not None and "hidden" in sql_obj.variable_options[key]:
            continue
        string = string + first_lowercase(key) + ":" + get_ts_type(key, sql_obj.variable_names) + ";\n"
    string = string + "}"

    if includeQuery:
        string = string + "export interface " + sql_obj.title + """Api
    {
      pageCount: number;
      """ + first_lowercase(sql_obj.title) + """: """ + sql_obj.title + """[];
    }
    """
