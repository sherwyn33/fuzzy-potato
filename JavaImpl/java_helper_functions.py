def get_type(key: str, variables: dict) -> str:
    if "varchar" in variables[key].lower():
        return "String"
    elif "bigint" in variables[key].lower():
        return "long"
    elif "int" in variables[key].lower():
        return "int"
    elif "decimal" in variables[key].lower():
        return "BigDecimal"
    elif "datetime" in variables[key].lower():
        return "LocalDateTime"
    elif "date" in variables[key].lower():
        return "LocalDate"
    elif "bit" in variables[key].lower():
        return "Boolean"
    elif "varbinary" in variables[key].lower():
        return "byte[]"
    return "String"


