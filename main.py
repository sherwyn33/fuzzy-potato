# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from collections import defaultdict
from typing import List

from Angular.advanced.create_ts_advanced import create_table_selection_table, create_table_selection_ts, \
    create_table_selection_api
from Angular.create_ts_api import create_ts_api
from Angular.create_ts_component import create_ts_component
from Angular.create_ts_html import create_ts_html
from Angular.create_ts_object import create_ts_object
from JavaImpl.Lists.create_impl_list import get_java_impl_list
from JavaImpl.Lists.create_java_list_api import create_java_api_list
from JavaImpl.create_java_api import create_java_api
from JavaImpl.create_java_dao import create_interface
from JavaImpl.create_java_impl import get_java_impl
from JavaImpl.create_java_object import get_java_object
from global_helper_functions import get_title_name
from dash import Dash
from dash import dcc
from dash import html

## hidden, matchip, matselect, datepicker, textarea, template (preselected text to select from)

def create_text(name):
    # Use a breakpoint in the code line below to debug your script.

    table = """
Create TABLE dbo.LoanAmendNewFixedComponent
(
    LoanAmendNewFixedComponentId bigint identity  --identity
        constraint PK_LoanAmendNewFixedComponent_LoanAmendNewFixedComponentId
            primary key,
    AustinLoanAmendID bigint,  --idselector --hidden
    DrawDownDate Date,  --datepicker
    Amount DECIMAL(18,4), 
    Term VarChar(5),  --matselect
    Rate DECIMAL(18,4),
    Ccm DECIMAL(18,4)
)
"""
    title = ""
    lines = table.splitlines()
    variable_names = dict()
    options = dict()
    # variable_name is the key and variable_type is the result
    for line in lines:
        if len(line) <= 3:
            continue

        variable_name = line.split()[0].replace(',', "").strip()
        variable_type = line.split()[1].replace(',', "").strip()

        if variable_name.lower() == "create":
            title = get_title_name(line)
            table_name = line.split()[2].split('.', 1)[1].replace('.', "")

        if not variable_name.lower() in get_junk_names():
            # if table_name.lower() + "id" == variable_name.lower():
            #     variable_type = variable_type + " identity"
            variable_names[variable_name] = variable_type
            options[variable_name] = get_options(line)

    # print(options)
    if name == 'impl':
        string = get_java_impl(table_name, title, variable_names, options)
        print(string)
    elif name == 'impllist':
        print(get_java_impl_list(table_name, title, variable_names, options))
    elif name == 'dao':
        print(create_interface(title))
    elif name == 'object':
        print(get_java_object(title, variable_names, options))
    elif name == 'japi':
        print(create_java_api(title))
    elif name == 'japilist':
        print(create_java_api_list(title))
    elif name == 'tsobj':
        print(create_ts_object(title, variable_names, options))
    elif name == 'tsapi':
        print((create_ts_api(title)))
    elif name == 'ahtml':
        print((create_ts_html(title, options)))
    elif name == 'ats':
        print(create_ts_component(title, options))

    elif name == 'selectTable':
        print(create_table_selection_table(title, options))
        print(create_table_selection_ts(title, options))
        print(create_table_selection_api(title, options))



def get_junk_names():
    return ["constraint", "primary", ")", "(", "create"]


def get_options(line: str) -> List[str]:
    options = line.split(' --')
    if options is None:
        return [""]
    return [o.strip() for o in options[1:]]

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # create_text('impl')
    create_text('selectTable')

# impl, dao, object, japi, tsobj, tsapi, ahtml, ats
