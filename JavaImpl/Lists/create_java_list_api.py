from global_helper_functions import first_lowercase


def create_java_api_list(title: str) -> str:
    return get_imports() + create_constructor(title) + "\n" + create_get_request(title) + "\n" + create_update_request(
        title) + "}"


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
    return '@Path("update' + title + """s")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    public int[] update""" + title + "s(List<" + title + """> request) throws SQLException {
        return this.""" + first_lowercase(title) + "Dao." + "Update" + title + """s(request);
    }
    """


def create_get_request(title: str) -> str:
    return '@Path("/{requestId}/get' + title + """s")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public List<""" + title + "> get" + title + """s(@PathParam("requestId") long[] requestId) {
        return this.""" + first_lowercase(title) + "Dao." + "Get" + title + """s(requestId);
    }
    """
