from global_helper_functions import first_lowercase


def create_interface(title: str):
    return """import java.sql.SQLException;

    public interface """ + title + """Dao
{
    long Update""" + title + "(" + title + " " + first_lowercase(title) + """) throws SQLException ;
    
    """ + title + " " + "Get" + title + """(int id);
}"""