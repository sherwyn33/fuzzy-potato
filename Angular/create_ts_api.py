def create_ts_api(title: str) -> str:
    return create_imports() + create_constructor(title) + create_get_api(title) + create_update_api(title) + '}'


def create_imports() -> str:
    return """import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

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
    return this.http.get<""" + title + ">(`/api/" + title + "/${id}/get" + title + """`);
}

"""


def create_update_api(title: str):
    return "update(request: " + title + """): Observable<number>
{
        return this.http.put<number>(`/api/""" + title + "/update" + title + """`, request);
}
"""


