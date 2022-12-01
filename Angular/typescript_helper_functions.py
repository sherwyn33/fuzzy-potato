import re

from global_helper_functions import add_quotation_marks, first_lowercase


def get_ts_type(key: str, variables: dict) -> str:
    if "varchar" in variables[key].lower():
        return "string"
    elif "bigint" in variables[key].lower():
        return "number"
    elif "int" in variables[key].lower():
        return "number"
    elif "decimal" in variables[key].lower():
        return "number"
    elif "date" in variables[key].lower():
        return "Date"
    elif "datetime" in variables[key].lower():
        return "Date"
    elif "bit" in variables[key].lower():
        return "boolean"
    return "string"


def variable_title(variable: str) -> str:
    return re.sub(r"(\w)([A-Z])", r"\1 \2", variable)


def quotation_variable(title: str, variable: str) -> str:
    return add_quotation_marks(full_name(title, variable))


def full_name(title: str, variable: str) -> str:
    return first_lowercase(title) + "." + first_lowercase(variable)
