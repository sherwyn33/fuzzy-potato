# gets the string for the constructor
from collections import defaultdict
from typing import List

from JavaImpl.java_helper_functions import get_type
from sql_object_detail import SqlObjectDetail
from global_helper_functions import first_lowercase, sql_by_type, add_quotation_marks


def get_java_impl(sql_obj_list: List[SqlObjectDetail]) -> str:

    for sql_obj in sql_obj_list:
        for key in sql_obj.variable_options:
            if "hidden" in sql_obj.variable_options[key]:
                sql_obj.variable_names.pop(key)
    sql_obj_read, sql_obj_write = sql_by_type(sql_obj_list)
    includeQuery = False
    if "filterTable" in sql_obj_read.options:
        includeQuery = True

    title = sql_obj_read.title
    string = get_constructor(title) + "\n\n" + create_get_function(sql_obj_read.table_name, title, sql_obj_read.variable_names, sql_obj_read.variable_options) + "\n\n" + \
           create_update_function(sql_obj_write.table_name, title, sql_obj_write.variable_names, sql_obj_write.variable_options) +\
            '\n' + get_local_date_text()
    if includeQuery:
        string = string + "\n\n" + create_query_function(sql_obj_read.table_name, title, sql_obj_read.variable_names, sql_obj_read.variable_options)

    return string + "\n" + "}"


def get_constructor(title: str):
    return """import nz.co.bnz.marginchange.app.loans.DataAccessException;
import javax.inject.Inject;
import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;

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
    elif "datetime" in variables[key].lower():
        return 'toLocalDateTime(rs.getTimestamp("' + key + '"))'
    elif "date" in variables[key].lower():
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

                return readResultAs""" + title + """s(rs).stream().findFirst().orElse(null);
            } catch (SQLException e) {
                throw new DataAccessException(e);
            }
        }
        catch (SQLException e) {
            throw new DataAccessException(e);
        }
    }

    private List<""" + title + """> readResultAs""" + title + "s(ResultSet rs)" + """ throws SQLException {
        List<""" + title + """> result = new ArrayList<>();
        while (rs.next()) {
            """ + title + """ r = """ + get_object_builder(title, variables) + """;
            result.add(r);
        }
        return result;
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
    elif "datetime" in variables[key].lower():
        return "stmt.setTimestamp(++c, command." + first_lowercase(
            key) + "() != null ? Timestamp.valueOf(command." + first_lowercase(key) + "()) : null);"
    elif "date" in variables[key].lower():
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
    }
        
    private LocalDateTime toLocalDateTime(Timestamp localDateTime)
    {
        return localDateTime == null ? null : localDateTime.toLocalDateTime();
    }
    """


def create_query_function(table_name: str, title: str, variables: dict, options: dict):
    filters = {key: options[key] for key in options if "filters" in options[key]}
    fuzzysearch = {key: options[key] for key in options if "fuzzysearch" in options[key]}
    search = {key: options[key] for key in options if "search" in options[key]}
    filter_from = {key: options[key] for key in options if "filter_from" in options[key]}
    filter_to = {key: options[key] for key in options if "filter_to" in options[key]}

    inputs = "int pageSize, int page, String sort, String order, "
    where = " WHERE "
    statements = ""

    for key in filters:
        inputs = inputs + "List<" + get_type(key, variables) + "> " + key + "List, "
        where = where + key + """ in (" + String.join(",", """ + key + """List) + ") AND """

    if len(fuzzysearch) > 0:
        statements = statements + """String escapedString = search.replace("%", "[%]");\n"""
        inputs = inputs + "String search, "
        where = where + " ("
        for key in fuzzysearch:
            where = where + key + " LIKE ? OR "
            statements = statements + """stmt.setString(++c, "%" + escapedString + "%");\n"""
        where = where[:-4]
        where = where + ") AND "

    for key in filter_from:
        where = where + key + """ > ? AND """
        inputs = inputs + "BigDecimal " + key + "FromFilter, "
        statements = statements + "stmt.setBigDecimal(++c, " + key + "FromFilter" + ");\n"

    for key in filter_to:
        where = where + key + """ < ? AND """
        inputs = inputs + "BigDecimal " + key + "ToFilter, "
        statements = statements + "stmt.setBigDecimal(++c, " + key + "ToFilter" + ");\n"

    statements2 = statements.replace("stmt","stmt2")

    for key in search:
        inputs = inputs + variables[key] + " " + first_lowercase(key) + ", "
        where = where + "(" + key + " LIKE ? OR " + key + "LIKE IS NULL) AND "

    search_vars = {key: variables[key] for key in search.keys()}
    statements = statements + get_recordset_setters(search_vars)
    statements = statements + """           
            stmt.setInt(++c, page * pageSize);
            stmt.setInt(++c, pageSize);
            """
    inputs = inputs[:-2]
    where = where[:-5] + '" '

    string = """    @Override
    public """ + title + "Api GetByQuery(" + inputs + """) {
        String sql = "Select """ + get_variable_name_list(variables, options) + \
           "FROM " + table_name + where + """
         + " Order By " + getOrderBy(sort, order) + 
         " OFFSET (?) ROWS FETCH NEXT (?) ROWS ONLY";
        String sqlCount = "Select  COUNT(1) As Count \\n" + 
        "FROM """ + table_name + add_quotation_line() + where + """;
                try (Connection conn = ds.getConnection() ;
             PreparedStatement stmt = conn.prepareStatement(sql);
             PreparedStatement stmt2 = conn.prepareStatement(sqlCount)) {
            int c= 0;
            """ + statements + """            
            try (ResultSet rs = stmt.executeQuery()) {
                List<""" + title + """> result = readResultAs""" + title + """s(rs);
                if (result.isEmpty())
                    result = null;
                c = 0;
                """ + statements2 + """
                try (ResultSet rs2 = stmt2.executeQuery()) {
                    int count = 0; 
                    if (rs2.next())
                        count = rs2.getInt("Count");
                    return new """ + title + """Api(count, result);
                    }
                }
            }
            catch (SQLException e) {
                throw new DataAccessException(e);
            }
    }
    
    private String getOrderBy(String sort, String order) {
        HashMap<String, String> sortMap = new HashMap<>();
        """
    for key in variables:
        string = string + "sortMap.put(" + add_quotation_marks(first_lowercase(key)) + ", " + add_quotation_marks(key) + ");\n"

    string = string + """HashMap<String, String> orderMap = new HashMap<>();
    orderMap.put("asc", "asc");
    orderMap.put("desc", "desc");

        return sortMap.get(sort) + " " + orderMap.get(order);
    }"""

    return string

