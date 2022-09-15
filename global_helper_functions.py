# gets the title to use in class names
def get_title_name(line: str):
    title = line.split()[2].split('.', 1)[1].replace('.', "")
    if title[-1].lower() == "s":
        return title.rstrip(title[-1])
    return title


def first_lowercase(string: str) -> str:
    return string[0].lower() + string[1:]


def add_quotation_marks(string: str) -> str:
    return '"' + string + '"'
