# gets the title to use in class names
from collections import defaultdict
from typing import List, Dict

from sql_object_detail import SqlObjectDetail


def get_title_name(line: str, char_remove):
    title = line.split()[2].split('.', 1)[1].replace('.', "").lstrip(char_remove)
    if title[-2:].lower() == "es":
        return title[:-2]
    if title[-1].lower() == "s":
        return title.rstrip(title[-1])
    return title


def get_type(line: str):
    return line.split()[1]


def first_lowercase(string: str) -> str:
    return string[0].lower() + string[1:]


def add_quotation_marks(string: str) -> str:
    return '"' + string + '"'


def find_table_name(word: str, lines: List[str]):
    for line in lines:
        word_list = line.split(" ")
        index = word_list.index(word) if word in word_list else None
        if index is not None:
            return word_list[index - 1]


def sql_by_type(sql_obj_list: List[SqlObjectDetail]) -> (SqlObjectDetail, SqlObjectDetail):
    sql_obj_read = [x for x in sql_obj_list if ("read" in x.options or "readwrite" in x.options)]
    sql_obj_write = [x for x in sql_obj_list if ("write" in x.options or "readwrite" in x.options)]
    if len(sql_obj_read) == 0:
        sql_obj_read = [sql_obj_list[-1]]
    if len(sql_obj_write) == 0:
        sql_obj_write = sql_obj_read
    return sql_obj_read[0], sql_obj_write[0]


def combine_sql_list(sql_obj_list: List[SqlObjectDetail]) -> SqlObjectDetail:
    sql_read, sql_write = sql_by_type(sql_obj_list)
    sql_read.variable_options = combine_dict(sql_read.variable_options, sql_write.variable_options, True)
    sql_read.variable_names = combine_dict(sql_read.variable_names, sql_write.variable_names, False)
    sql_read.options = list(set(sql_read.options + sql_write.options))
    return sql_read


def combine_dict(d1: dict, d2: dict, is_list: bool = True) -> dict:
    dd = defaultdict(list)

    if not is_list:
        for d in (d1, d2):
            for key, value in d.items():
                if value in dd[key]:
                    continue
                dd[key].append(value)
            for key, value in dd.items():
                dd[key] = ''.join(map(str, value))
    else:
        for d in (d1, d2):
            for key, value in d.items():
                if value in dd[key]:
                    continue
                dd[key].extend(value)
    return dd
