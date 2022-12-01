from typing import List

from Angular.create_ts_html import get_input
from global_helper_functions import sql_by_type
from sql_object_detail import SqlObjectDetail


def create_ts_mhtml(sql_object_list: List[SqlObjectDetail]) -> str:
    sql_obj, sql_obj_write = sql_by_type(sql_object_list)
    return create_header(sql_obj.title) + create_fields(sql_obj.title, sql_obj_write.variable_options) + create_footer()



def create_header(title: str) -> str:
    return """<div class="modal-header">
  <h4 class="modal-title">Title</h4>
  <button type="button" class="close" aria-label="Close" (click)="dialogRef.close()">
    <span aria-hidden="true">&times;</span>
  </button>
</div>
<div class="modal-body">
  <p>Description.</p>
  <div>"""

def create_footer() -> str:
    return """
<div class="modal-footer">
  <button name="submit" (click)="submit()" mat-raised-button color="bnz-primary" type="submit" >Submit</button>
</div>
"""


def create_fields(title: str, options: dict) -> str:
    string = ""
    for key in options:
        string = string + get_input(title, key, options)
    return string

