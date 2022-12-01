from Angular.typescript_helper_functions import variable_title
from global_helper_functions import first_lowercase
from sql_object_detail import SqlObjectDetail

def create_import(sql_object_detail: SqlObjectDetail) -> str:
    return create_cell_map(sql_object_detail) + "\n" + create_header_map(sql_object_detail)

def create_cell_map(sql_object_detail: SqlObjectDetail) -> str:
    string = """    private static Map<String, CellProcessor> getCellProcessorMap()
    {
        CellProcessor optionalBigDecimal = new Optional(new ParseBigDecimal());
        CellProcessor optionalInt = new Optional(new ParseInt());
        CellProcessor optionalBool = new Optional(new ParseBool("yes", "no"));
        CellProcessor optionalDate = new Optional(usingIsoDate());
        ImmutableMap.Builder<String, CellProcessor> cellProcessors = ImmutableMap.builder();
        """
    return string + "\n" + get_cell_map_line(sql_object_detail) + "return cellProcessors.build();\n}"


def create_header_map(sql_object_detail: SqlObjectDetail) -> str:
    string = """    private static Map<String, String> getHeaderMap()
    {
        Map<String, String> headerMappings = new HashMap<>();
        """
    return string + get_header_map_line(sql_object_detail) + "return headerMappings;\n}\n"


def get_cell_map_line(sql_object_detail: SqlObjectDetail) -> str:
    string = ""
    names = sql_object_detail.variable_names
    for key in names:
        if "date" in names[key].lower():
            string = string + 'cellProcessors.put("' + first_lowercase(key) + '", optionalDate);\n'
        if "decimal" in names[key].lower():
            string = string +  'cellProcessors.put("' + first_lowercase(key) + '", optionalBigDecimal);\n'
        if "int" in names[key].lower():
            string = string +  'cellProcessors.put("' + first_lowercase(key) + '", optionalInt);\n'
        if "bit" in names[key].lower():
            string = string +  'cellProcessors.put("' + first_lowercase(key) + '", optionalBool);\n'
    return string


def get_header_map_line(sql_object_detail: SqlObjectDetail) -> str:
    string = ""
    names = sql_object_detail.variable_names
    for key in names:
        string = string + 'headerMappings.put("' + variable_title(key) + '", "' + key + '");\n'
    return string