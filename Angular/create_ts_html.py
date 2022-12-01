from typing import List

from Angular.typescript_helper_functions import variable_title, quotation_variable
from sql_object_detail import SqlObjectDetail
from global_helper_functions import add_quotation_marks, first_lowercase, sql_by_type


def create_ts_html(sql_object_list: List[SqlObjectDetail]) -> str:
    sql_obj, _ = sql_by_type(sql_object_list)
    return create_header(sql_obj.title) + create_fields(sql_obj.title, sql_obj.variable_options) + create_footer()


def create_header(title: str) -> str:
    return """<div class="section">
  <h1>Tile</h1>
  <p>Description</p>
  <h4 *ngIf=" """ + first_lowercase(title) + """ == null" shimmer>Fetching data...</h4>
  <form *ngIf=" """ + first_lowercase(title) + '!=null" #f1="ngForm" (ngSubmit)="submit(\'Submitted\')">\n'

def create_footer() -> str:
    return """
        <br>
    <button id="submit" name="submit" mat-raised-button color="bnz-primary" type="submit" [disabled]="f1.invalid" [hidden]="workFlow.status != 'Created'">Submit</button>
    <button id="complete" name="submit" mat-raised-button color="bnz-primary" type="button" (click)="submit('Completed')" [disabled]="f1.invalid" [hidden]="workFlow.status != 'Submitted'">Complete</button>
    <button id="save" name="save" mat-raised-button color="bnz-primary" type="button" (click)="submit('Created')" [hidden]="workFlow.status != 'Created'">Save and Exit</button>
    <button id="delete" name="delete" mat-raised-button color="bnz-primary" type="button" (click)="delete()" [hidden]="!(workFlow.status=='Created' || workFlow.status=='Submitted')">Delete/Reject</button>
  </form>
</div>
"""


def create_fields(title: str, options: dict) -> str:
    string = ""
    for key in options:
        string = string + get_input(title, key, options)
    return string


def get_input(title: str, key: str, options: dict) -> str:
    option = options[key]
    string = ""
    if option:
        if "read" in option:
            return string
        if "hidden" in option:
            return string
        if "identity" in option:
            return string
        if "matselect" in option:
            string = string + """
            <mat-form-field style="min-width: 300px">
                    <mat-select [(value)]=""" + quotation_variable(title, key) + " placeholder=" + add_quotation_marks(variable_title(key)) + """ [disabled]="isDisabled">
                    <mat-option value="null">Please select</mat-option>
                </mat-select>
            </mat-form-field>
            """
        if "datepicker" in option:
            string = string + """
                  <mat-form-field style="min-width: 300px">
        <input matInput [matDatepicker]=""" + add_quotation_marks(first_lowercase(key)) + """ placeholder=""" + add_quotation_marks(variable_title(key)) + """
              name=""" + add_quotation_marks(first_lowercase(key)) + """ [(ngModel)]=""" + quotation_variable(title, key) + """ required [disabled]="isDisabled">
        <mat-datepicker-toggle matSuffix [for]=""" + add_quotation_marks(first_lowercase(key)) + """></mat-datepicker-toggle>
        <mat-datepicker #""" + first_lowercase(key) + """ [disabled]="isDisabled"></mat-datepicker>
      </mat-form-field>
      """
        if "matslide" in option:
            string = """
                  <mat-slide-toggle name="""  + add_quotation_marks(first_lowercase(key)) + """ [(ngModel)]=""" + quotation_variable(title, key) + \
            ' labelPosition="before" color="primary" [disabled]="isDisabled">' + variable_title(key) + '</mat-slide-toggle>\n'
        if "checkbox" in option:
            string = """    <br>
                  <mat-checkbox name="""  + add_quotation_marks(first_lowercase(key)) + """ [(ngModel)]=""" + quotation_variable(title, key) + \
            ' labelPosition="before" color="primary" [disabled]="isDisabled">\n<span class="text-wrap">' + variable_title(key) + '</span></mat-checkbox>\n'
        if "matchip" in option:
            string = string + """
        <div>
      <mat-form-field class="chip-list" appearance="fill">
        <mat-label>Type and hit enter to add """ + variable_title(key) + """</mat-label>
        <mat-chip-list #chipList aria-label="Selection">
          <mat-chip
            *ngFor="let input of selected""" + key + """"
            (removed)="remove""" + key + """(input)">
            {{input}}
            <button matChipRemove class="close"[disabled]="isDisabled">
              <span aria-hidden="true">&times;</span>
            </button>
          </mat-chip>
          <input
            #""" + first_lowercase(key) + """Input
            [formControl]=""" + add_quotation_marks(first_lowercase(key) + "Ctrl") + """
            [matChipInputFor]="chipList"
            [matChipInputSeparatorKeyCodes]="separatorKeysCodes"
            (matChipInputTokenEnd)="type""" + key + """($event)"
            [disabled]="isDisabled"
          >
        </mat-chip-list>
        </mat-form-field>
    <mat-divider></mat-divider>

    </div>
            """
        if "textarea" in option:
            string = string + """
             <br><br>
           <mat-form-field class="text-half-width">
            <textarea class="text-full-width" name=""" + add_quotation_marks(
            first_lowercase(key)) + """ [(ngModel)]=""" + quotation_variable(title, key) + """ matInput
                       placeholder=""" + add_quotation_marks(variable_title(key)) + """
                       cdkTextareaAutosize
                       maxlength="500"
                       #autosize="cdkTextareaAutosize"
                       cdkAutosizeMinRows="1"
                       cdkAutosizeMaxRows="8" [disabled]="isDisabled"></textarea>
           </mat-form-field>
               """
        if "template" in option:
            string = string + """
          <button  type="button" mat-raised-button color="bnz-primary" (click) = "open""" + key + """Template()" [disabled]="isDisabled">Select Templates</button>
          """
        if "email-selector" in option:
            string = string + """<app-email-selector name=""" + add_quotation_marks(first_lowercase(key)) + """ [(ngModel)]="this.selected""" + key + """" [isDisabled]="isDisabled"
                        [customer]="this.workFlow.customer" [bis]="this.workFlow.bis"></app-email-selector>"""
        if "autocomplete" in option:
            string = string + """<mat-form-field style="min-width: 250px">
            <h5 class="mat-cell">""" + key + """</h5>
            <input type="text" [matAutocomplete]=auto""" + key + """ [(ngModel)]=""" + quotation_variable(title, key) + """ (ngModelChange)="filter""" + key + """($event)"
                   matInput placeholder="">
            <mat-autocomplete #auto""" + key + """="matAutocomplete">
              <mat-option *ngFor="let option of filtered""" + key + """ " [value]="option.""" + first_lowercase(key) + """ ">
                {{option.""" + first_lowercase(key) + """}}
              </mat-option>
            </mat-autocomplete>
          </mat-form-field>
"""
    if string == "":
        return """
        <mat-form-field>
            <input name=""" + add_quotation_marks(first_lowercase(key)) + ' [(ngModel)]=' + quotation_variable(title, key)+ """ [disabled] = "isDisabled" matInput
            placeholder=""" + add_quotation_marks(variable_title(key)) + """>
        </mat-form-field>"""
    return string


