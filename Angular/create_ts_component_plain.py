from typing import List

from Angular.create_ts_component import create_autocomplete
from Angular.typescript_helper_functions import full_name
from sql_object_detail import SqlObjectDetail
from global_helper_functions import first_lowercase, combine_sql_list


def create_ts_component_plain(sql_object_list: List[SqlObjectDetail]) -> str:
    sql_obj = combine_sql_list(sql_object_list)
    return create_constructor(sql_obj) + create_init(sql_obj) + create_get_data(sql_obj) + create_submit_data(
            sql_obj.title, sql_obj.variable_options) \
               + create_template(sql_obj.title, sql_obj.variable_options) + create_matchip(
            sql_obj.title, sql_obj.variable_options) + create_autocomplete(sql_obj) + create_generic_functions(sql_obj.title) +"\n}"


def create_constructor(sql_obj: SqlObjectDetail) -> str:
    string = """export class """ + sql_obj.title + """Component implements OnInit, OnDestroy, AfterViewInit {
     """ + first_lowercase(sql_obj.title) + """ : """ + sql_obj.title + """ = <""" + sql_obj.title + """>{};
  isDisabled: boolean;
  """
    chip_options = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "matchip" in sql_obj.variable_options[key]}
    if bool(chip_options):
        string = string + "separatorKeysCodes: number[] = [ENTER, COMMA, SPACE];\n @ViewChild('autosize') autosize: CdkTextareaAutosize;"
        for key in chip_options:
            string = string + "\nselected" + key + """: string[] = [];
          """ + first_lowercase(key) + """Ctrl = new FormControl('');
          """
    email_options = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "email-selector" in sql_obj.variable_options[key]}
    if bool(email_options):
        for key in email_options:
            string = string + "\nselected" + key + """: string[] = [];
          """
    autocomplete_options = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "autocomplete" in sql_obj.variable_options[key]}
    for key in autocomplete_options:
        string = string + "\nfiltered" + key + ": [];\n"

    string = string + "constructor(private " + first_lowercase(sql_obj.title) + "Service:" + sql_obj.title + """Service,
                    private router: Router,
                    private route: ActivatedRoute,
                    private dialog: MatDialog
            )
            {
            }
            """
    return string


def get_ng_onInit() -> str:
    return """
    ngOnInit(): void {
    """

def get_update_by_url(title: str) -> str:
    return """    
    private updateFromParams(p: ParamMap)
    {
        const q = Number(p.get('q'));

        if (q !== null && !isNaN(q) && q > 0)
        {
          this.workFlow.referenceId = q;
          this.get""" + title + """(q);
        }
  }
  
  updateParams()
  {
    const extras: NavigationExtras = {
      relativeTo: this.route,
      queryParams: {
        q: this.workFlow.referenceId
      },
      queryParamsHandling: 'merge',
    };

    this.router.navigate([], extras)
      .catch(s => {
        console.log(s);
        return Promise.resolve(false);
      });
  }"""

def create_init(sql_obj: SqlObjectDetail) -> str:
    string = get_ng_onInit()

    mat_slide = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "matslide" in sql_obj.variable_options[key]};

    if bool(mat_slide):
        for key in mat_slide:
            string = string + "this." + full_name(sql_obj.title, key) + " = false;\n"

    if "workflow" in sql_obj.options:
        string = string + get_update_by_url(sql_obj.title)

    if "modal" in sql_obj.options:
        string = string + "this.get" + sql_obj.title + "(this.data?.id);"
    return string + """
}
"""


def create_get_data(sql_obj:SqlObjectDetail) -> str:
    string = "if (id != null){"
    string = string + """  private get""" + sql_obj.title + """(id: number) {
    this.""" + first_lowercase(sql_obj.title) + """Service.get(id).subscribe(data => {
    this.""" + first_lowercase(sql_obj.title) + """ = data;
    }"""
    if "workflow" in sql_obj.options:
        string = string + """
    if (this.workFlow.status != "Created") {
        this.isDisabled = true;
    }
    """

    string = string + setup_fields_on_get(sql_obj.title, sql_obj.variable_options)
    return string + " \n});\n}"


def setup_fields_on_get(title: str, options: dict) -> str:
    date_options = {key: options[key] for key in options if "datepicker" in options[key]}
    string = ""
    for key in date_options:
        string = string + "this." + full_name(title, key) + " = new Date(this." + full_name(title, key) + ");\n"

    chip_options = {key: options[key] for key in options if
                    ("matchip" in options[key] or "email-selector" in options[key])}
    for key in chip_options:
        string = string + """
      if (this.""" + full_name(title, key) + """ != null && this.""" + full_name(title, key) + """ != "") {
        this.selected""" + key + "= this." + full_name(title, key) + """.split(',')
      }
        """
    return string


def create_submit_data(title: str, options: dict) -> str:
    string = """
    submit(): void {
    this.updateDate();
    """
    chip_options = {key: options[key] for key in options if
                    ("matchip" in options[key] or "email-selector" in options[key])}
    for key in chip_options:
        string = string + "this." + full_name(title, key) + " = this.selected" + key + """.join(", ").replace(" ", "");
        """

    string = string + "this." + first_lowercase(title) + "Service.update(this." + first_lowercase(title) + """).subscribe(() => {
      if (this.""" + first_lowercase(title) + """.Id > 0) {
          alert("Item successfully updated.");
      }
      else {
          alert("Item successfully created.");
      }
    }, () => alert("Failed to update item."));
      """
    return string + "}\n"


def create_template(title: str, options: dict) -> str:
    template_options = {key: options[key] for key in options if "template" in options[key]}
    string = ""
    for key in template_options:
        string = string + """
    open""" + key + """Template(){
        this.dialog.open(SelectionDialogComponent, {
          width: '900px',
          minWidth: '650px',
          maxHeight: '700px',
          data: {
            templateText: """ + title + """Component.get""" + key + """Templates()
          }
        }).afterClosed().subscribe(result => {
            if (result) {
              this.""" + full_name(title, key) + """= (this.""" + full_name(title, key) + """?? "") + result.join("\\n") + "\\n"
            }
          }
        );
    }
        
    private static get""" + key + """Templates(): string[] {
        return [
        "option 1"
        ]
    }
    """
    return string


def create_matchip(title: str, options: dict) -> str:
    matchip_options = {key: options[key] for key in options if "matchip" in options[key]}
    string = ""
    for key in matchip_options:
        string = string + "\ntype" + key + """(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();

    if (value) {
      this.selected""" + key + """.push(value);
    }

    // Clear the input value
    event.chipInput!.clear()

    this.""" + first_lowercase(key) + """Ctrl.setValue(null);

    if (this.""" + full_name(title, key) + """ != null && this.""" + full_name(title, key) + """.length > 0) {
      this.""" + full_name(title, key) + """ = this.""" + full_name(title, key) + """ + " " + value;
    }
    else {
      this.""" + full_name(title, key) + """ = value;
    }
  }
  
    remove""" + key + """(input: string){
    const index = this.selected""" + key + """.indexOf(input);

    if (index >= 0) {
      this.selected""" + key + """.splice(index, 1);
    }
  }
  """
    return string


def create_generic_functions(title: str):
    return """
  private updateDate() {
    const now = moment();
    this.""" + first_lowercase(title) + """.dateUpdated = toDate(now);
  }"""
