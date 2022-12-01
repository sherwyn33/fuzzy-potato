from typing import List

from global_helper_functions import first_lowercase, combine_sql_list
from sql_object_detail import SqlObjectDetail

def create_constructor(sql_obj: SqlObjectDetail) -> str:
    string = """export class """ + sql_obj.title + """Component implements OnInit, OnDestroy, AfterViewInit {
  searchField = new FormControl('');
  resultDataSource: """ + sql_obj.title + """[] = [];
    @ViewChild(MatPaginator) paginator: MatPaginator;
    @ViewChild(MatSort) sort: MatSort;
  private filterSubscription: Subscription;
    isLoadingResults: boolean;
  resultsLength = 0;
  pageSize: number = 10;
  pageIndex: number = 0;
  activeSort: string = 'view';
  sortDirection: SortDirection = 'desc';
  
    user: User;
"""
    string = string + "\n displayedColumns = [" + get_variable_name_list(sql_obj.variable_options) + "];\n"
    date_filter_to = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "filter_to" in sql_obj.variable_options[key] and "datetime" in sql_obj.variable_names[key]}
    number_filter_to = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "filter_to" in sql_obj.variable_options[key] and "datetime" not in sql_obj.variable_names[key]}
    date_filter_from = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "filter_from" in sql_obj.variable_options[key] and "datetime" in sql_obj.variable_names[key]}
    number_filter_from = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "filter_from" in sql_obj.variable_options[key] and "datetime" not in sql_obj.variable_names[key]}

    for key in date_filter_to:
        string = string + key + "ToFilter: Moment = moment().add(2, 'weeks');"
    for key in date_filter_from:
        string = string + key + "FromFilter: Moment = moment();"
    for key in number_filter_to:
        string = string + key + "ToFilter: int = 100"
    for key in number_filter_from:
        string = string + key + "FromFilter: int = 0"
    string = string + "constructor(private " + first_lowercase(sql_obj.title) + "Service:" + sql_obj.title + """Service,
                    private router: Router,
            )
            {
            }
      ngOnInit(): void {
    if (!this.authService.hasRights('VIEW')) {
      this.router.navigate(['/error']);
    }
    
    
        this.user = AuthService.getSessionUser();
    }
            """
    return string




def create_table_selection_ts(sql_object_list: List[SqlObjectDetail]) -> str:
    string = ""
    sql_obj = combine_sql_list(sql_object_list)
    string = string + first_lowercase(sql_obj.title) + "DataSource = new MatTableDataSource<" + sql_obj.title + ">();\n"
    string = string + "  @ViewChild('" + sql_obj.title + "table') " + sql_obj.title + "Table: MatTable<any>;\n\n"
    selection_option = list({key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "idselector" in sql_obj.variable_options[key]}.items())[0]

    string = string + "\n displayed" + sql_obj.title + "Columns = [" + get_variable_name_list(sql_obj.variable_options) + ", 'button'];\n"

    string = string + "private get" + sql_obj.title + """(){
        this.""" + first_lowercase(sql_obj.title) + """Service.get""" + sql_obj.title + """(this.workFlow.referenceId).subscribe(result => {
        if (result != null){
         this.""" + first_lowercase(sql_obj.title) + """DataSource.data = result;
        }
        });
        }
        """
    string = string + "private update" + sql_obj.title + """(id){
        this.""" + first_lowercase(sql_obj.title) + """DataSource.data.forEach(f => f.""" + selection_option[0] + """ = id)
        this.""" + first_lowercase(sql_obj.title) + """Service.update""" + sql_obj.title + """(this.""" + first_lowercase(sql_obj.title) + """DataSource.data);
        }

        """

    return string + """remove""" + sql_obj.title + """(index: number): void {
    if (index >= 0) {
      this.""" + first_lowercase(sql_obj.title) + """DataSource.data.splice(index, 1);
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


def get_query_pipe(sql_obj: SqlObjectDetail) -> str:
    string = ""
    string = string + """
    
      ngAfterViewInit() {
        // If the user changes the sort order, reset back to the first page.
        this.sort.sortChange.subscribe(() => (this.paginator.pageIndex = 0));
    
        merge(this.sort.sortChange, this.paginator.page, this.searchField.valueChanges)
          .pipe(
            startWith({}),
            switchMap(() => {
              this.isLoadingResults = true;
              const query = this.getQuery();
              this.updateParams(query);
              return this.""" + sql_obj.title + """Service.getFilteredItems(
                query
              );
            }),
            map(data => {
              // Flip flag to show that loading has finished.
              this.isLoadingResults = false;
    
              if (data === null) {
                return [];
              }
    
              // Only refresh the result length if there is new data. In case of rate
              // limit errors, we do not want to reset the paginator to zero, as that
              // would prevent users from re-triggering requests.
              this.resultsLength = data.pageCount;
              return data.workflows;
            }), f
          )
          .subscribe(data => (this.resultDataSource = data));
      }
      
        getQuery(): HttpParams {
        let params = new HttpParams()
          .set('sort', this.sort.active)
          .set('order', this.sort.direction)
          .set('page', this.paginator.pageIndex)
          .set('pageSize', this.paginator.pageSize);
    
        if (this.filterText != null) {
          params = params.append('search', this.filterText);
        } 
        """
    date_filter_to = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "filter_to" in sql_obj.variable_options[key]}

    for key in date_filter_to:
        string = string + "params = params.appendAll({'dateShelved': [this." +  first_lowercase(key) + " .year(), " \
                       "this." +  first_lowercase(key) + ".month() + 1, this." +  first_lowercase(key) + ".date()]});"

    string = string + """
    
        }
        
  private setFiltersFromUrl(p: ParamMap) {
    if (p.has('sort') && p.has('order')) {
      this.activeSort = p.get('sort');
      this.sortDirection =  p.get('order') as SortDirection;
    }
    if (p.has('page') && p.has('pageSize')) {
      this.pageIndex = Number(p.get('page'));
      this.pageSize = Number(p.get('pageSize'));
    }
   
    if (p.has('search')) {
      this.filterText = p.get('search');
      this.searchField.setValue(this.filterText);
    }
  }
        """


    return string + "\nreturn params;\n}"

