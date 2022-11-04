# gets the string for the constructor
from collections import defaultdict
from typing import List

from sql_object_detail import SqlObjectDetail
from global_helper_functions import first_lowercase, sql_by_type


def get_java_impl(sql_obj_list: List[SqlObjectDetail]) -> str:
    for sql_obj in sql_obj_list:
        for key in sql_obj.variable_options:
            if "hidden" in sql_obj.variable_options[key]:
                sql_obj.variable_names.pop(key)
    sql_obj_read, sql_obj_write = sql_by_type(sql_obj_list)
    title = sql_obj_read.title
    return get_constructor(title) + "\n\n" + create_get_function(sql_obj_read.table_name, title, sql_obj_read.variable_names, sql_obj_read.variable_options) + "\n\n" + \
           create_update_function(sql_obj_write.table_name, title, sql_obj_write.variable_names, sql_obj_write.variable_options) + '\n' + get_local_date_text() + "\n" + "}"


def get_constructor(title: str):
    return """import nz.co.bnz.marginchange.app.loans.DataAccessException;
import javax.inject.Inject;
import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.LocalDate;

    public class """ + title + "DaoImpl implements " + title + "Dao \n" \
           + "{\n" + """    private final DataSource ds;
    @Inject
    public """ + title + """DaoImpl(DataSource ds)
    {
        this.ds = ds;
    }"""


# Gets select a,b,c,d string
def get_variable_name_list(variables: dict, options: dict, index=0, skip_id: bool = False, ) -> str:
    i = index
    max_char = 120
    string = ""
    start = True
    for key in variables:
        if skip_id and start:
            start = False
            continue
        if options[key] is not None and "hidden" in options[key]:
            continue
        i = i + len(key) + 2
        if i > max_char:
            string = string + add_quotation_line()
            i = 0
        string = string + key + ", "
    string = string[:-2]
    if i > 0:
        return string + add_quotation_line()
    return string



def get_object_builder(title: str, variables: defaultdict):
    string = title + ".newBuilder()"
    for key in variables:
        string = string + "\n\t\t ." + first_lowercase(key) + "(" + get_recordset_getter(key, variables) + ")"
    return string + ".build()"


# getters
def get_recordset_getter(key: str, variables: dict):
    if "varchar" in variables[key].lower():
        return 'rs.getString("' + key + '")'
    elif "bigint" in variables[key].lower():
        return 'rs.getLong("' + key + '")'
    elif "int" in variables[key].lower():
        return 'rs.getInt("' + key + '")'
    elif "decimal" in variables[key].lower():
        return 'rs.getBigDecimal("' + key + '")'
    elif "date" in variables[key].lower():
        return 'toLocalDate(rs.getDate("' + key + '"))'
    elif "datetime" in variables[key].lower():
        return 'toLocalDate(rs.getDate("' + key + '"))'
    elif "bit" in variables[key].lower():
        return 'rs.getBoolean("' + key + '")'
    elif "varbinary" in variables[key].lower():
        return 'rs.getBytes("' + key + '")'
    return 'rs.getObject("' + key + '")'


def create_get_function(table_name: str, title: str, variables: dict, options: dict):
    selection_option = list({key: options[key] for key in options if "idselector" in options[key]}.items())
    selector = title + "ID";
    if len(selection_option) > 0:
        selector = selection_option[0][0]
    return """    @Override
    public """ + title + " Get" + title + """(int id) {
        String sql = "Select """ + get_variable_name_list(variables, options) + \
           "FROM " + table_name + " WHERE " + selector + r'=?";' + """
                try (Connection conn = ds.getConnection() ;
             PreparedStatement stmt = conn.prepareStatement(sql)) {
             stmt.setInt(1, id);
            try (ResultSet rs = stmt.executeQuery()) {

                return readResultAs""" + title + """(rs);
            } catch (SQLException e) {
                throw new DataAccessException(e);
            }
        }
        catch (SQLException e) {
            throw new DataAccessException(e);
        }
    }

    private """ + title + """ readResultAs""" + title + "(ResultSet rs)" + """ throws SQLException {
        if (rs.next()) {
            return """ + get_object_builder(title, variables) + """;
        }
        return null;
    }"""


def add_quotation_line() -> str:
    return r' "' + "\n + " + r'"'


def create_update_function(table_name: str, title: str, variables: dict, options: dict) -> str:
    string = """ @Override
    public long Update""" + title + "(" + title + """ command) throws SQLException { \n"""
    string = string + r'String sql = "Merge ' + table_name + r' As p' + add_quotation_line() + 'Using' + add_quotation_line() + '(VALUES (' + \
             create_question_marks(len(variables)) + ")) s" + add_quotation_line()
    string = string + "(" + get_variable_name_list(variables, options) + ") " + "ON p." + title + "Id = s." + title + r'Id' \
             + add_quotation_line()
    string = string + "WHEN NOT MATCHED THEN " + add_quotation_line() + "INSERT " + "(" + get_variable_name_list(variables, options, 0, True)\
             + ") VALUES " + "(" + get_variable_name_list(variables, options, 0, True) + ") "
    string = string + "WHEN MATCHED THEN Update Set " + get_update_variables(variables, 60, True) \
             + " Output inserted." + title + r'Id As Id;";' + "\n" + """
         try (Connection conn = ds.getConnection()) {
            conn.setAutoCommit(false);
            try (
                    PreparedStatement stmt = conn.prepareStatement(sql)) {
                int c = 0;
                """ + get_recordset_setters(variables) + """ 
                ResultSet rs = stmt.executeQuery();
                long id;
                if (rs.next()){
                    id = rs.getLong("Id");
                }
                else {
                    conn.rollback();
                    throw new RuntimeException("");
                }
                conn.commit();
                return id;
                } catch (SQLException e) {
                conn.rollback();
                throw new RuntimeException(e);
            }
        }
    }"""
    return string


def get_recordset_setters(variables: dict) -> str:
    string = ""
    for key in variables:
        string = string + get_recordset_setter(key, variables) + "\n"
    return string


def get_recordset_setter(key: str, variables: dict) -> str:
    if "varchar" in variables[key].lower():
        return "stmt.setString(++c, command." + first_lowercase(key) + "());"
    elif "bigint" in variables[key].lower():
        return "stmt.setLong(++c, command." + first_lowercase(key) + "());"
    elif "int" in variables[key].lower():
        return "stmt.setInt(++c, command." + first_lowercase(key) + "());"
    elif "decimal" in variables[key].lower():
        return "stmt.setBigDecimal(++c, command." + first_lowercase(key) + "());"
    elif "date" in variables[key].lower():
        return "stmt.setDate(++c, command." + first_lowercase(
            key) + "() != null ? java.sql.Date.valueOf(command." + first_lowercase(key) + "()) : null);"
    elif "datetime" in variables[key].lower():
        return "stmt.setDate(++c, command." + first_lowercase(
            key) + "() != null ? java.sql.Date.valueOf(command." + first_lowercase(key) + "()) : null);"
    elif "bit" in variables[key].lower():
        return "stmt.setBoolean(++c, command." + first_lowercase(key) + "());"
    elif "varbinary" in variables[key].lower():
        return "stmt.setBytes(++c, command." + first_lowercase(key) + "());"
    return "stmt.setObject(++c, command." + first_lowercase(key) + "());"


def get_update_variables(variables: dict, index: int, skip_id: int = False):
    i = index
    max_char = 120
    string = ""
    start = True
    for key in variables:
        if skip_id and start:
            start = False
            continue
        i = i + len(key) * 2 + 5
        string = string + key + " = s." + key + ", "
        if i > max_char:
            string = string + add_quotation_line()
            i = 0
    if i > 0:
        string = string[:-2]
        return string + add_quotation_line()
    string = string[:-9]
    return string


def create_question_marks(count: int) -> str:
    string = "?"
    max_char = 120
    i = 0
    for x in range(count - 1):
        i = i + 2
        string = string + ", ?"
        if i > max_char:
            string = string + "/n"
    return string


def add_new_line_plus_comma() -> str:
    return r""", \n" +  """ + '\n "'


def get_local_date_text():
    return """
    private LocalDate toLocalDate(Date date)
    {
        if (date == null)
            return null;

        return date.toLocalDate();
    }"""
