from typing import List

from JavaImpl.java_helper_functions import get_type
from global_helper_functions import first_lowercase, sql_by_type
from sql_object_detail import SqlObjectDetail


def create_java_api(sql_obj_list: List[SqlObjectDetail]) -> str:
    sql_obj_read, sql_obj_write = sql_by_type(sql_obj_list)
    title = sql_obj_read.title
    includeQuery = False
    if "filterTable" in sql_obj_read.options:
        includeQuery = True

    string = get_imports() + create_constructor(title) + "\n" + create_get_request(title) + "\n" + create_update_request(
        title)
    if includeQuery:
        string = string + create_query_request(title, sql_obj_read)
    return string + '}'


def get_imports() -> str:
    return """
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.sql.SQLException;
import java.time.LocalDate;
import java.util.List;
import javax.inject.Inject;
import javax.inject.Named;
import javax.ws.rs.Consumes;
import javax.ws.rs.DefaultValue;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.PUT;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.MediaType;

    """


def create_constructor(title: str) -> str:
    string = '@Path("/' + title + '/")\n'
    string = string + "public class " + title + """Resource
{
    private final """ + title + "Dao " + first_lowercase(title) + """Dao;
    
    @Inject
    public """ + title + "Resource(" + title + "Dao " + first_lowercase(title) + """Dao)
    {
        this.""" + first_lowercase(title) + "Dao = " + first_lowercase(title) + """Dao;
    }
    """
    return string


def create_update_request(title: str) -> str:
    return '@Path("update' + title + """")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    public long update""" + title + "(" + title + """ request) throws SQLException {
        return this.""" + first_lowercase(title) + "Dao." + "Update" + title + """(request);
    }
    """


def create_get_request(title: str) -> str:
    return '@Path("/{requestId}/get' + title + """")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public """ + title + " get" + title + """(@PathParam("requestId") int requestId) {
        return this.""" + first_lowercase(title) + "Dao." + "Get" + title + """(requestId);
    }
    """


def create_query_request(title: str, sql_obj_read: SqlObjectDetail) -> str:
    options = sql_obj_read.variable_options
    filters = {key: options[key] for key in options if "filters" in options[key]}
    filter_from = {key: options[key] for key in options if "filter_from" in options[key]}
    filter_to = {key: options[key] for key in options if "filter_to" in options[key]}
    fuzzysearch = {key: options[key] for key in options if "fuzzysearch" in options[key]}
    search = {key: options[key] for key in options if "search" in options[key]}
    inputs = "pageSize, page, sort, order, "

    string = """@GET
    @Produces(MediaType.APPLICATION_JSON)
    public """ + title + "Api" + """ GetByQuery(@QueryParam("sort") String sort,
                                    @QueryParam("order") String order,
                                    @QueryParam("page") int page,
                                    @QueryParam("pageSize") int pageSize,
                                    """
    for key in filters:
        inputs = inputs + key + "List, "
        string = string + '@QueryParam("' + first_lowercase(key) + '") List<' + get_type(key, sql_obj_read.variable_names) + '> ' + first_lowercase(key) + "List,\n"

    if len(fuzzysearch) > 0:
        inputs = inputs + "search, "
        string = string + '@QueryParam("search") String search,\n'

    for key in search:
        inputs = inputs + key + ", "
        string = string + '@QueryParam("' + first_lowercase(key) + '") ' + get_type(key, sql_obj_read.variable_names) + ' ' + first_lowercase(key) + ",\n"

    for key in filter_from:
        inputs = inputs + first_lowercase(key + "FromFilter") + ", "
        string = string + '@QueryParam("' + first_lowercase(key + "FromFilter") + '") ' + get_type(key, sql_obj_read.variable_names) + ' ' + first_lowercase(key + "FromFilter") + ",\n"

    for key in filter_to:
        inputs = inputs + first_lowercase(key + "ToFilter") + ", "
        string = string + '@QueryParam("' + first_lowercase(key + "ToFilter") + '") '  + get_type(key, sql_obj_read.variable_names) + ' ' + first_lowercase(key + "ToFilter") + ",\n"

    string = string[:-2] + "){\n"
    inputs = inputs[:-2]

    return string + "return this." + first_lowercase(title) + "Dao.GetByQuery(" + inputs + """);
    }
    """

