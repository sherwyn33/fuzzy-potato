from typing import List

from JavaImpl.java_helper_functions import get_type
from sql_object_detail import SqlObjectDetail
from global_helper_functions import first_lowercase, combine_sql_list


def get_java_object(sql_object_list: List[SqlObjectDetail]) -> str:
    sql_obj = combine_sql_list(sql_object_list)
    for key in sql_obj.variable_options:
        if "hidden" in sql_obj.variable_options[key]:
            sql_obj.variable_names.pop(key)
    return get_imports() + get_object_fields(sql_obj.title, sql_obj.variable_names) + create_private_builder(sql_obj.title, sql_obj.variable_names) + \
             "\n\n" + create_public_getters(sql_obj.variable_names) + create_static_builder_text(sql_obj.title, sql_obj.variable_names) + "\n}"


def get_imports():
    return """
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.google.common.collect.ImmutableList;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

"""


def get_object_fields(title: str, variables: dict) -> str:
    string = """
@JsonInclude(JsonInclude.Include.NON_NULL)
public class """ + title + "\n{\n"

    for key in variables:
        string = string + "private final " + get_type(key, variables) + " " + first_lowercase(key) + ";" + "\n"
    return string


def create_private_builder(title: str, variables: dict):
    string = "@JsonCreator\n"
    string = string + "private " + title + "(Builder b)" + "\n{\n"

    for key in variables:
        string = string + "this." + first_lowercase(key) + " = b." + first_lowercase(key) + ";\n"

    return string + "\n\t}"


def create_public_getters(variables: dict) -> str:
    string = ""
    for key in variables:
        string = string + """@JsonProperty
        public """ + get_type(key, variables) + " " + first_lowercase(key) + "() { return " + first_lowercase(
            key) + ";}\n\n"
    return string


def create_static_builder_text(title: str, variables: dict) -> str:
    string = """public static Builder newBuilder()
    {
        return new Builder();
    }
    
    public static class Builder
    {
    """

    for key in variables:
        string = string + "\t@JsonProperty\n\t private " + get_type(key, variables) + " " + first_lowercase(key) + ";\n\n"

    string = string + """
        private Builder()
        {
        }
"""

    for key in variables:
        string = string + """
        public Builder """ + first_lowercase(key) + "(" + get_type(key, variables) + " " + first_lowercase(key) + """)
        {
            this.""" + first_lowercase(key) + " = " + first_lowercase(key) + """;
            return this;
        }\n"""

    string = string + "\npublic " + title + """ build()
        {
            return new """ + title + """(this);
        }
    }"""

    return string
