from typing import List

from Angular.create_ts_html import get_input
from Angular.typescript_helper_functions import variable_title
from sql_object_detail import SqlObjectDetail
from global_helper_functions import first_lowercase, add_quotation_marks, sql_by_type, combine_sql_list


def create_table_selection_api(sql_object_list: List[SqlObjectDetail]):
    sql_obj, _ = sql_by_type(sql_object_list)
    return create_get_api(sql_obj.title) + create_update_api(sql_obj.title)

def create_get_api(title: str) -> str:
    return "get" + title + "(id: number): Observable<" + title + """[]>
{
    return this.http.get<""" + title + "[]>(`/api/" + title + "/${id}/get" + title + """s`);
}

"""


def create_update_api(title: str):
    return "update" + title + "(request: " + title + """[]): Observable<number[]>
{
        return this.http.put<number[]>(`/api/""" + title + "/update" + title + """s`, request);
}
"""

def create_table_selection_table(sql_object_list: List[SqlObjectDetail]):
    string = ""
    sql_obj, _ = sql_by_type(sql_object_list)
    string = string + """ <div id=" """ + sql_obj.title + """-div">
        <h4 class="filter-headers">""" + sql_obj.title + """</h4>
            <table #""" + sql_obj.title + """Table id="search-results" mat-table [dataSource]=" """ + first_lowercase(sql_obj.title) + """DataSource" matSort>
    """
    for key in sql_obj.variable_options:
        string = string + """  <ng-container matColumnDef=""" + add_quotation_marks(key) + """>
        <th mat-header-cell *matHeaderCellDef  mat-sort-header>""" + variable_title(key) + """</th>
        <td mat-cell *matCellDef="let """ + first_lowercase(sql_obj.title) + """">
         """ + get_input(sql_obj.title, key, sql_obj.variable_options) + """
        </td>
      </ng-container>
      """

    string = string + """<ng-container matColumnDef="button">
        <th mat-header-cell *matHeaderCellDef></th>
        <td mat-cell *matCellDef="let i = index">
        <button class="button-margins" (click)=""" + add_quotation_marks("remove" + sql_obj.title + "(i)") + """>Delete</button>
        </td>
      </ng-container>"""

    string = string + """
        <tr mat-header-row *matHeaderRowDef="displayed""" + sql_obj.title + """Columns"></tr>
        <tr mat-row *matRowDef="let """ + first_lowercase(sql_obj.title) + """; columns: displayed""" + sql_obj.title + """Columns;"></tr>
       </table>
    <br>
    <button mat-raised-button color="bnz-primary" type="button" (click)="add""" + sql_obj.title + """()" [hidden]="!(workFlow.status=='Created' || workFlow.status=='Submitted')">Add New</button>
    </div>"""

    return string
