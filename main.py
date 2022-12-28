# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from typing import List
# import numpy as np
from Angular.advanced.create_modal import create_ts_mhtml
from Angular.advanced.create_ts_advanced import create_table_selection_table, \
    create_table_selection_api
from Angular.create_ts_api import create_ts_api
from Angular.create_ts_component import create_ts_component
from Angular.create_ts_component_plain import create_ts_component_plain
from Angular.create_ts_html import create_ts_html
from Angular.create_ts_object import create_ts_object
from Angular.create_ts_table import create_table
from Angular.create_ts_table_html import create_filter_table_html
from JavaImpl.Imports import create_import
from JavaImpl.Lists.create_impl_list import get_java_impl_list
from JavaImpl.Lists.create_java_list_api import create_java_api_list
from JavaImpl.create_java_api import create_java_api
from JavaImpl.create_java_dao import create_interface
from JavaImpl.create_java_impl import get_java_impl
from JavaImpl.create_java_object import get_java_object
from sql_object_detail import SqlObjectDetail
from global_helper_functions import get_title_name, get_type, find_table_name, sql_by_type


## hidden, matchip, matselect, datepicker, textarea, template (preselected text to select from)

def create_text(name):
    # Use a breakpoint in the code line below to debug your script.

    table = """Create TABLE dbo.AustinDrawdownSchedule
(
    AustinDrawdownScheduleId bigint identity
        constraint PK_AustinDrawdownSchedule_AustinDrawdownScheduleId
            primary key,
    AustinLoanRequestsID bigint,
    DrawDownDate Date,
    Amount DECIMAL(18,4),
    TypeId int,
    TermRateVANote VarChar(30),
    Term VarChar(5),  --matselect,
    Rate  DECIMAL(18,4),
    InterestOnlyYears DECIMAL(18,4),
    AmortTerm DECIMAL(18,4),
    IsDeleted Bit not  null constraint DF_AustinDrawdownSchedule_IsDeleted Default(0)
"""
    lines = table.splitlines()

    sql_object_list = list()
    sql_obj = SqlObjectDetail()
    sql_obj.variable_names = dict()
    # variable_name is the key and variable_type is the result
    for idx, line in enumerate(lines):
        if len(line) <= 3:
            continue

        variable_name = line.split()[0].replace(',', "").strip()

        if variable_name.lower() == "create":
            if len(sql_obj.variable_names) > 0:
                sql_object_list.append(sql_obj)

            sql_obj = SqlObjectDetail()
            sql_obj.sql_type = get_type(line)
            sql_obj.title = get_title_name(line, "v" if sql_obj.sql_type.lower() == "view" else "")
            sql_obj.table_name = line.split()[2].split('.', 1)[1].replace('.', "")
            sql_obj.options = get_options(line)

        if not variable_name.lower() in get_junk_names():
            if sql_obj.sql_type.lower() == "view":
                table_ref = variable_name.split(".", 1)[:1][0]
                table_name = find_table_name(table_ref, lines[idx:]).split(".", 1)[1:][0]
                variable_name = variable_name.split(".", 1)[1:][0].strip()
                variable_type = [(x.variable_names[variable_name]) for x in sql_object_list if (x.table_name == table_name)]
                sql_obj.variable_names[variable_name] = variable_type[0]
                sql_obj.variable_options[variable_name] = get_options(line)
            else:
                variable_type = line.split()[1].replace(',', "").replace(" ", "")
                sql_obj.variable_names[variable_name] = variable_type
                sql_obj.variable_options[variable_name] = get_options(line)


    sql_object_list.append(sql_obj)
    sql_obj_read, _ = sql_by_type(sql_object_list)
    title = sql_obj_read.title
    includeQuery = False
    if "filterTable" in sql_obj_read.options:
        includeQuery = True
    if len(sql_object_list) == 0:
        raise Exception("Unable to process sql objects")

    isWorkflow = False
    if "workflow" in sql_obj_read.options:
        isWorkflow = True

    if name == 'impl':
        string = get_java_impl(sql_object_list)
        print(string)
    elif name == 'impllist':
        print(get_java_impl_list(sql_object_list))
    elif name == 'dao':
        print(create_interface(title))
    elif name == 'object':
        print(get_java_object(sql_object_list))
    elif name == 'japi':
        print(create_java_api(sql_object_list))
    elif name == 'japilist':
        print(create_java_api_list(title))
    elif name == 'tsobj':
        print(create_ts_object(sql_object_list))
    elif name == 'tsapi':
        print((create_ts_api(sql_object_list)))
    elif name == 'ahtml':
        if includeQuery:
            print(create_filter_table_html(sql_object_list))
        else:
            print((create_ts_html(sql_object_list)))
    elif name == 'ats':
        if includeQuery:
            print(create_table(sql_obj_read))
        else:
            if isWorkflow:
                print(create_ts_component(sql_object_list))
            else:
                print(create_ts_component_plain(sql_object_list))
    elif name == 'mahtml':
        print(create_ts_mhtml(sql_object_list))
    elif name == 'selectTable':
        print(create_table_selection_table(sql_object_list))
        print(create_table_selection_ts(sql_object_list))
        print(create_table_selection_api(sql_object_list))
    elif name == 'import':
        print(create_import(sql_obj_read))


def get_junk_names():
    return ["constraint", "primary", ")", "(", "create", "references", "select", "from", "inner", "join", "left", "right", "outter"]


def get_options(line: str) -> List[str]:
    options = line.split(' --')
    if options is None:
        return [""]
    return [o.strip() for o in options[1:]]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # create_text('object')
    create_text('impllist')
    # create_text('dao')
    # create_text('japi')
    # create_text('tsapi')
    # create_text('tsobj')
    # create_text('mahtml')
    # create_text('ats')
    # create_text('import')

# impl, dao, object, japi, tsobj, tsapi, ahtml, ats
