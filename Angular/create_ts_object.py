from Angular.typescript_helper_functions import get_ts_type
from global_helper_functions import first_lowercase


def create_ts_object(title: str, variables: dict, options: dict) -> str:
    string = """export interface """ + title + "\n {\n"
    for key in variables:
        if options[key] is not None and "hidden" in options[key]:
            continue
        string = string + first_lowercase(key) + ":" + get_ts_type(key, variables) + ";\n"
    return string + "}"
