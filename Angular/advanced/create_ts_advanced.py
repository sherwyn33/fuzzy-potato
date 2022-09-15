from Angular.create_ts_component import setup_fields_on_get
from Angular.create_ts_html import get_input
from Angular.typescript_helper_functions import full_name, variable_title
from global_helper_functions import first_lowercase, add_quotation_marks, get_title_name


def create_table_selection_api(title: str, options: dict):
    return create_get_api(title) + create_update_api(title)


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


def create_table_selection_ts(title: str, options: dict):
    string = first_lowercase(title) + "DataSource = new MatTableDataSource<" + title + ">();\n"
    string = string + "  @ViewChild('" + title + "table') " + title + "Table: MatTable<any>;\n\n"
    selection_option = list({key: options[key] for key in options if "idselector" in options[key]}.items())[0]

    string = string + "\n displayed" + title + "Columns = [" + get_variable_name_list(options) + ", 'button'];\n"

    string = string + "private get" + title + """(){
        this.""" + first_lowercase(title) + """Service.get""" + title + """(this.workFlow.referenceId).subscribe(result => {
        if (result != null){
         this.""" + first_lowercase(title) + """DataSource.data = result;
        }
        });
        }
        """
    string = string + "private update" + title + """(id){
        this.""" + first_lowercase(title) + """DataSource.data.forEach(f => f.""" + selection_option[0] + """ = id)
        this.""" + first_lowercase(title) + """Service.update""" + title + """(this.""" + first_lowercase(title) + """DataSource.data);
        }
        
        """

    return string + """remove""" + title + """(index: number): void {
    if (index >= 0) {
      this.""" + first_lowercase(title) + """DataSource.data.splice(index, 1);
    } 
  }
  
  """


def get_variable_name_list(options: dict) -> str:
    string = ""
    for key in options:
        if options[key] is not None and ("hidden" in options[key] or "identity" in options[key]):
            continue
        string = string + "'" + key + "' , "
    string = string[:-2]
    return string


def create_table_selection_table(title: str, options: dict):
    string = """ <div id=" """ + title + """-div">
    <h4 class="filter-headers">""" + title + """</h4>
        <table #""" + title + """Table id="search-results" mat-table [dataSource]=" """ + first_lowercase(title) + """DataSource" matSort>
"""
    for key in options:
        string = string + """  <ng-container matColumnDef=""" + add_quotation_marks(key) + """>
        <th mat-header-cell *matHeaderCellDef  mat-sort-header>""" + variable_title(key) + """</th>
        <td mat-cell *matCellDef="let """ + first_lowercase(title) + """">
         """ + get_input(title, key, options) + """
        </td>
      </ng-container>
      """

    string = string + """<ng-container matColumnDef="button">
        <th mat-header-cell *matHeaderCellDef></th>
        <td mat-cell *matCellDef="let i = index">
        <button class="button-margins" (click)=""" + add_quotation_marks("remove" + title + "(i)") + """>Delete</button>
        </td>
      </ng-container>"""

    string = string + """
        <tr mat-header-row *matHeaderRowDef="displayed""" + title + """Columns"></tr>
        <tr mat-row *matRowDef="let """ + first_lowercase(title) + """; columns: displayed""" + title + """Columns;"></tr>
       </table>
    <br>
    <button mat-raised-button color="bnz-primary" type="button" (click)="add""" + title + """()" [hidden]="!(workFlow.status=='Created' || workFlow.status=='Submitted')">Add New</button>
    </div>"""

    return string
