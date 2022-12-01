from typing import List

from Angular.create_ts_html import create_fields
from global_helper_functions import first_lowercase, combine_sql_list, add_quotation_marks, sql_by_type
from sql_object_detail import SqlObjectDetail

def create_filter_table_html(sql_obj_list: SqlObjectDetail) -> str:
    sql_obj_read, sql_obj_write = sql_by_type(sql_obj_list)

    return create_filter(sql_obj_read) + create_table_section(sql_obj_read) + create_create_new_section(sql_obj_write)

def create_filter(sql_obj: SqlObjectDetail) -> str:
    string = '<div id="' + sql_obj.title + '" class="mat-typography">'

    string = string + """<mat-tab-group>
    <mat-tab label="History">
     <div id="history-div">
       <br>
       <mat-card>
        <mat-card-title class="filter-headers">Filters</mat-card-title>
        """
    date_filter_to = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if
                      "filter_to" in sql_obj.variable_options[key] and "datetime" in sql_obj.variable_names[key]}
    number_filter_to = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if
                        "filter_to" in sql_obj.variable_options[key] and "datetime" not in sql_obj.variable_names[key]}
    date_filter_from = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if
                        "filter_from" in sql_obj.variable_options[key] and "datetime" in sql_obj.variable_names[key]}
    number_filter_from = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if
                          "filter_from" in sql_obj.variable_options[key] and "datetime" not in sql_obj.variable_names[
                              key]}

    for key in date_filter_to:
        string = string + """
                   <mat-form-field class="float filter-field">
             <input matInput [matDatepicker]="picker" (dateChange)="reload()"
                    [(ngModel)]=""" + add_quotation_marks(first_lowercase(key + "ToFilter")) + """ readonly>
             <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
             <mat-label class="filter-label">""" + first_lowercase(key + "ToFilter") + """</mat-label>
             <mat-datepicker #picker disabled="false"></mat-datepicker>
           </mat-form-field>"""
    for key in date_filter_from:
        string = string + """
                   <mat-form-field class="float filter-field">
             <input matInput [matDatepicker]="picker" (dateChange)="reload()"
                    [(ngModel)]=""" + add_quotation_marks(first_lowercase(key + "FromFilter")) + """ readonly>
             <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
             <mat-label class="filter-label">""" + first_lowercase(key + "ToFilter") + """</mat-label>
             <mat-datepicker #picker disabled="false"></mat-datepicker>
           </mat-form-field>"""

    for key in number_filter_to:
        string = string + """                   
        <mat-form-field class="float filter-field">
             <input [(ngModel)]=""" + add_quotation_marks(first_lowercase(key + "ToFilter")) + """ matInput autocomplete="off">
        </mat-form-field>
        """
    for key in number_filter_from:
        string = string + """                   
        <mat-form-field class="float filter-field">
             <input [(ngModel)]=""" + add_quotation_marks(first_lowercase(key + "FromFilter")) + """ matInput autocomplete="off">
        </mat-form-field>
        """

    string = string + """    
        <mat-form-field class="filter" appearance="standard">
          <mat-label>Search</mat-label>
          <input [(ngModel)]="filterText" (keyup.enter)="reload()" matInput autocomplete="off">
        </mat-form-field>
         <div class="mat-form-field">
           <button name="search" mat-raised-button color="bnz-primary" (click)="reload()">Search</button>
           <button name="search" mat-raised-button color="warn" (click)="clear()">Clear</button>
         </div>
       </mat-card>
       """
    return string


def create_table_section(sql_obj: SqlObjectDetail) -> str:
    string = """       
    <div class="mat-elevation-z8">
      <table id="search-results" mat-table [dataSource]="resultDataSource"
             matSort [matSortActive]="activeSort" matSortDisableClear [matSortDirection]="sortDirection">"""
    main_table = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if
                      "main_table" in sql_obj.variable_options[key]}
    for key in main_table:
        string = string + """
        <ng-container matColumnDef=""" + add_quotation_marks(first_lowercase(key)) + """>
          <th mat-header-cell *matHeaderCellDef mat-sort-header disableClear>#</th>
          <td class="btn-link" mat-cell *matCellDef="let row"> {{row.""" + first_lowercase(key) + """}} </td>
        </ng-container>"""

    string = string + """
          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr class="element-row"  mat-row *matRowDef="let row; columns: displayedColumns;"  matRipple [cdkDetailRow]="row" [cdkDetailRowTpl]="tpl"></tr>
      </table>
    <mat-paginator [length]="resultsLength" [pageIndex]="pageIndex" [pageSize]="pageSize" [pageSizeOptions]="[5, 10, 25, 100]" aria-label="Select page"></mat-paginator>
        """
    string = string + """
           <ng-template #tpl let-row>
         <td class="mat-row detail-row" [@detailExpand]  [attr.colspan]="displayedColumns.length" style="overflow: hidden">
           <table>
             <tr>"""

    sub_table = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if
                      "sub_table" in sql_obj.variable_options[key]}

    for key in sub_table:
        string = string + """   
                <td><span class="font-weight-bold margin-left">""" + key + """: </span> {{row.""" + first_lowercase(key) + """}}
"""
    string = string + """
               </tr>
           </table>
           <br>
         </td>
       </ng-template>
       </div>
      </div>

    </mat-tab>
    """
    return string


def create_create_new_section(sql_obj: SqlObjectDetail) -> str:
    form_start_options = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "form_start" in sql_obj.variable_options[key]}
    string = """
        <mat-tab label="Create New">
      <div class="create-new">
      """

    string = string + create_fields(sql_obj.title, form_start_options)

    string = string + """
      <div class="mat-form-field">
        <button mat-raised-button color="bnz-primary" (click)="create()" [disabled]="isDisabled()">Create</button>
      </div>
          </div>
    </mat-tab>
  </mat-tab-group>

    </div>
    """
    return string
