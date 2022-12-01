from typing import List

from global_helper_functions import first_lowercase, sql_by_type
from sql_object_detail import SqlObjectDetail


def create_ts_api(sql_obj_list: List[SqlObjectDetail]) -> str:
    sql_obj_read, sql_obj_write = sql_by_type(sql_obj_list)
    title = sql_obj_read.title
    includeQuery = False
    if "filterTable" in sql_obj_read.options:
        includeQuery = True
    string = create_imports() + create_constructor(title) + create_get_api(title) + create_update_api(title)
    if includeQuery:
        string = string + create_query_api(title)
    return string + '}'


def create_imports() -> str:
    return """import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import {map} from "rxjs/operators";

"""

def create_constructor(title: str) -> str:
    string = """@Injectable({
  providedIn: 'root'
})
export class """
    return  string + title + """Service
{
      constructor(private http: HttpClient)
  {
  }
  
  """


def create_get_api(title: str) -> str:
    return "get(id: number): Observable<" + title + """>
{
    return this.http.get<""" + title + ">(`/api/" + first_lowercase(title) + "/${id}/get" + title + """`);
}

"""


def create_update_api(title: str):
    return "update(request: " + title + """): Observable<number>
{
        return this.http.put<number>(`/api/""" + first_lowercase(title) + "/update" + title + """`, request);
}
"""


def create_query_api(title: str):
    string = """  
    getFilteredItems(params: HttpParams): Observable<""" + title + """Api> {
    return this.http.get('/api/""" + first_lowercase(title) + """', {
      params: params
    }).pipe(
      map(res =>
      {
        if (res != null) {
          res["payload"] = res;
          return res["payload"];
        }
      })
    );
  }"""
    return string

