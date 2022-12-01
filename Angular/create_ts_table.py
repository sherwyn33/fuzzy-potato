from typing import List

from Angular.create_ts_component import create_template, create_matchip, create_autocomplete
from global_helper_functions import first_lowercase, combine_sql_list
from sql_object_detail import SqlObjectDetail


def create_table(sql_obj: SqlObjectDetail) -> str:
    return create_constructor(sql_obj) + create_query_pipe(sql_obj) + create_create_function(sql_obj) +\
           create_template(sql_obj.title, sql_obj.variable_options) + create_matchip(
            sql_obj.title, sql_obj.variable_options) + create_autocomplete(sql_obj) + "\n}"


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
  filterText: string;

    user: User;
"""
    main_table_options = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "main_table" in sql_obj.variable_options[key]}
    string = string + "\n displayedColumns = [" + get_variable_name_list(main_table_options) + "];\n"
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
        string = string + first_lowercase(key) + "ToFilter: Moment = moment().add(2, 'weeks');\n"
    for key in date_filter_from:
        string = string + first_lowercase(key) + "FromFilter: Moment = moment();\n"
    for key in number_filter_to:
        string = string + first_lowercase(key) + "ToFilter: number = 100\n"
    for key in number_filter_from:
        string = string + first_lowercase(key) + "FromFilter: number = 0\n"

    autocomplete_options = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "autocomplete" in sql_obj.variable_options[key]}
    for key in autocomplete_options:
        string = string + "\nfiltered" + key + ": [];"

    string = string + "constructor(private " + first_lowercase(sql_obj.title) + "Service:" + sql_obj.title + """Service,
                    private router: Router,
                  private route: ActivatedRoute,    
                            
                    private location: Location,
                    private authService: AuthService
            )
            {
            }
      ngOnInit(): void {
    if (!this.authService.hasRights('VIEW')) {
      this.router.navigate(['/error']);
    }
        this.user = AuthService.getSessionUser();    
        this.filterSubscription = this.route.queryParamMap.subscribe(p => this.setFiltersFromUrl(p));
    }
            """
    return string


def get_variable_name_list(options: dict) -> str:
    string = ""
    for key in options:
        if options[key] is not None and ("hidden" in options[key] or "identity" in options[key]):
            continue
        string = string + "'" + first_lowercase(key) + "', "
    string = string[:-2]
    return string


def create_query_pipe(sql_obj: SqlObjectDetail) -> str:
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
              return this.""" + first_lowercase(sql_obj.title) + """Service.getFilteredItems(
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
              return data.""" + first_lowercase(sql_obj.title) + """;
            }),
          )
          .subscribe(data => (this.resultDataSource = data));
      }

  
  ngOnDestroy(): void {
    this.filterSubscription.unsubscribe();
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
        string = string + "params = params.appendAll({'dateShelved': [this." + first_lowercase(
            key) + "ToFilter.year(), " \
                   "this." + first_lowercase(
            key) + ".month() + 1, this." + first_lowercase(key) + ".date()]});\n"
    for key in date_filter_from:
        string = string + "params = params.appendAll({'dateShelved': [this." + first_lowercase(
            key) + "FromFilter.year(), " \
                   "this." + first_lowercase(
            key) + ".month() + 1, this." + first_lowercase(key) + ".date()]});\n"

    for key in number_filter_to:
        string = string + "params.append('" + first_lowercase(key) + "ToFilter', this." + first_lowercase(
            key) + "ToFilter);\n"
    for key in number_filter_from:
        string = string + "params.append('" + first_lowercase(key) + "FromFilter', this." + first_lowercase(
            key) + "FromFilter);\n"

    string = string + """
        return params;
        }
        
  reload() {
    this.searchField.setValue(this.filterText);
    }
  
  updateParams(params: HttpParams){
    const url ='""" + sql_obj.title + """?' + params.toString();
    this.location.replaceState(url);
  }
  
  clear() {
    this.filterText = "";
    this.searchField.setValue(this.filterText);
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
  
        """

    for key in number_filter_to:
        string = string + """   
         if (p.has('""" + first_lowercase(key) + """ToFilter')){
      this.""" + first_lowercase(key) + """ToFilter = Number(p.get('""" + first_lowercase(key) + """ToFilter'));
        }"""

    for key in number_filter_from:
        string = string + """   
         if (p.has('""" + first_lowercase(key) + """FromFilter')){
      this.""" + first_lowercase(key) + """FromFilter = Number(p.get('""" + first_lowercase(key) + """FromFilter'));
        }"""

    return string + "\n}\n\n"


def create_create_function(sqlobj: SqlObjectDetail) -> str:
    string = first_lowercase(sqlobj.title) + ":" + sqlobj.title + ";"
    string = string = string + """
    
     isDisabled(): boolean {
        return false;
     }
     
    create(){
    if (this.""" + first_lowercase(sqlobj.title) + """!= null) {
    this.""" + first_lowercase(sqlobj.title) + "Service.update(this." + first_lowercase(
        sqlobj.title) + ")" + \
             ".subscribe()\n}\n}"
    return string
