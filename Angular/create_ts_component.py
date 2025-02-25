from typing import List

from Angular.typescript_helper_functions import full_name, quotation_variable
from sql_object_detail import SqlObjectDetail
from global_helper_functions import first_lowercase, combine_sql_list


def create_ts_component(sql_object_list: List[SqlObjectDetail]) -> str:
    sql_obj = combine_sql_list(sql_object_list)
    return create_constructor(sql_obj.title, sql_obj.variable_options) + create_init(sql_obj.title,
            sql_obj.variable_options) + create_get_data(sql_obj.title, sql_obj.variable_options) + create_submit_data(
            sql_obj.title, sql_obj.variable_options) \
               + create_delete_data() + create_template(sql_obj.title, sql_obj.variable_options) + create_matchip(
            sql_obj.title, sql_obj.variable_options) + create_autocomplete(sql_obj) + create_workflow_functions()


def create_constructor(title: str, options: dict) -> str:
    string = """
    workFlow : Workflow = <Workflow>{};
  """ + first_lowercase(title) + """ : """ + title + """ = <""" + title + """>{};
  private subscription: Subscription;
  isDisabled: boolean;
  """
    chip_options = {key: options[key] for key in options if "matchip" in options[key]}
    if bool(chip_options):
        string = string + "separatorKeysCodes: number[] = [ENTER, COMMA, SPACE];\n @ViewChild('autosize') autosize: CdkTextareaAutosize;"
        for key in chip_options:
            string = string + "\nselected" + key + """: string[] = [];
          """ + first_lowercase(key) + """Ctrl = new FormControl('');
          """
    email_options = {key: options[key] for key in options if "email-selector" in options[key]}
    if bool(email_options):
        for key in email_options:
            string = string + "\nselected" + key + """: string[] = [];
          """

    autocomplete_options = {key: options[key] for key in options if "autocomplete" in options[key]}
    for key in autocomplete_options:
        string = string + "\nfiltered" + key + ": [];"

    string = string + "constructor(private " + first_lowercase(title) + "Service:" + title + """Service,
                    private workflowService: WorkflowService,
                    private router: Router,
                    private route: ActivatedRoute,
                    private dialog: MatDialog
            )
            {
                this.workFlow = this.router.getCurrentNavigation().extras.state.workflow;
            }
            """
    return string


def create_init(title: str, options: dict) -> str:
    string = """
    ngOnInit(): void {
    this.subscription = this.route.queryParamMap.subscribe(p => this.updateFromParams(p));
    """
    mat_slide = {key: options[key] for key in options if "matslide" in options[key]};

    if bool(mat_slide):
        for key in mat_slide:
            string = string + "this." + full_name(title, key) + " = false;\n"

    return string + """if (this.workFlow.referenceId > 0){
      this.updateParams();
    }
}
    ngOnDestroy(): void
    {
    this.subscription.unsubscribe();
    }
    
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
  }
"""


def create_get_data(title: str, options: dict) -> str:
    string = """  private get""" + title + """(id: number) {
    this.""" + first_lowercase(title) + """Service.get(id).subscribe(data => {
    this.""" + first_lowercase(title) + """ = data;
    if (this.workFlow.status != "Created") {
        this.isDisabled = true;
    }
    """
    string = string + setup_fields_on_get(title, options)
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
    submit(status : string): void {
    this.setStatus(status);
    """
    chip_options = {key: options[key] for key in options if
                    ("matchip" in options[key] or "email-selector" in options[key])}
    for key in chip_options:
        string = string + "this." + full_name(title, key) + " = this.selected" + key + """.join(", ").replace(" ", "");
        """

    string = string + "this." + first_lowercase(title) + "Service.update(this." + first_lowercase(title) + """).subscribe((id) => {
        this.updateDate();
      if (this.workFlow.referenceId > 0) {
        this.workflowService.updateWorkflow(this.workFlow).subscribe(() => {
          alert("Workflow successfully updated.");
          this.router.navigateByUrl("/workflow");
        });
      }
      else {
        this.workFlow.referenceId = id;
        this.workflowService.updateWorkflow(this.workFlow).subscribe(() => {
          alert("Workflow successfully created.");
          this.router.navigateByUrl("/workflow");
        });
      }
    }, () => alert("Failed to update workflow."));
      """
    return string + "}\n"


def create_delete_data():
    return """delete(): void {
    this.updateDate();
    this.setStatus("Rejected");
    this.workflowService.updateWorkflow(this.workFlow).subscribe(() => alert("Workflow successfully rejected."));
  }
  """


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

def create_autocomplete(sql_obj: SqlObjectDetail):
    autocomplete_options = {key: sql_obj.variable_options[key] for key in sql_obj.variable_options if "autocomplete" in sql_obj.variable_options[key]}
    string = ""
    for key in autocomplete_options:
        string = string + """
        filter""" + key + """(evt: string) {
        evt = evt + "";
        if (!evt || this.""" + full_name(sql_obj.title, key) + """.length < 3) this.filtered""" + key + """ = [];
        else {
          this.update""" + key + """();
        }
      }
      
        update""" + key + """() {
    this.xxxService.find(this.""" + full_name(sql_obj.title, key) + """).subscribe(r => {
        if (r == null) {
          this.filtered""" + key + """ = []
          return;
        }
        this.filtered""" + key + """ = r;
        this.""" + full_name(sql_obj.title, key) + """ = this.""" + full_name(sql_obj.title, key) + """.trim();
        }
    );
  }"""

    return string


def create_workflow_functions():
    return """private setStatus(status: string){
    this.workFlow.status = status;
  }

  private updateDate() {
    const now = new Date();
    this.workFlow.dateUpdated = [now.getFullYear(), now.getMonth() + 1, now.getDate()];
  }"""
