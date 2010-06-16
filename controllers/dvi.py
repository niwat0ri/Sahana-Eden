# -*- coding: utf-8 -*-

"""
    DVI Module - Controllers
"""

module = "dvi"

if module not in deployment_settings.modules:
    session.error = T("Module disabled!")
    redirect(URL(r=request, c="default", f="index"))

# Only people with the DVI role should be able to access this module
#try:
#    dvi_group = db(db[auth.settings.table_group_name].role == "DVI").select().first().id
#    if auth.has_membership(dvi_group):
#        pass
#    else:
#        session.error = T("Not Authorised!")
#        redirect(URL(r=request, c="default", f="user", args="login"))
#except:
#    session.error=T("Not Authorised!")
#    redirect(URL(r=request, c="default", f="user", args="login"))

# Options Menu (available in all Functions" Views)
def shn_menu():
    response.menu_options = [
        [T("Recovery Requests"), False, URL(r=request, f="recreq"),[
            [T("List Requests"), False, URL(r=request, f="recreq")],
            [T("New Request"), False, URL(r=request, f="recreq", args="create")],
        ]],
        [T("Recovery Reports"), False, URL(r=request, f="body"),[
            [T("List Reports"), False, URL(r=request, f="body")],
            [T("New Report"), False, URL(r=request, f="body", args="create")],
        ]],
        [T("Search by ID Tag"), False, URL(r=request, f="body", args="search_simple")]
    ]
    menu_selected = []
    if session.rcvars and "dvi_body" in session.rcvars:
        body = db.dvi_body
        query = (body.id == session.rcvars["dvi_body"])
        record = db(query).select(body.id, body.pr_pe_label, limitby=(0,1)).first()
        if record:
            label = record.pr_pe_label
            menu_selected.append(["%s: %s" % (T("Body"), label), False,
                                 URL(r=request, f="body", args=[record.id])])
    if menu_selected:
        menu_selected = [T("Open recent"), True, None, menu_selected]
        response.menu_options.append(menu_selected)

shn_menu()

# S3 framework functions
def index():

    """ Module's Home Page """

    try:
        module_name = s3.modules[module]["name_nice"]
    except:
        module_name = T("Disaster Victim Identification")

    return dict(module_name=module_name)

def recreq():

    """ RESTful CRUD controller """

    response.s3.pagination = True

    def recreq_postp(jr, output):
        if jr.representation in ("html", "popup"):
            label = T("Update")
            linkto = shn_linkto(jr, sticky=True)("[id]")
            response.s3.actions = [
                dict(label=str(label), _class="action-btn", url=linkto)
            ]
        return output
    response.s3.postp = recreq_postp

    output = shn_rest_controller(module, "recreq", listadd=False)

    shn_menu()
    return output

def body():

    """ RESTful CRUD controller """

    response.s3.pagination = True

    def body_postp(jr, output):
        if jr.representation in ("html", "popup"):
            if not jr.component:
                label = T("Details")
            else:
                label = T("Update")
            linkto = shn_linkto(jr, sticky=True)("[id]")
            response.s3.actions = [
                dict(label=str(label), _class="action-btn", url=linkto)
            ]
        return output
    response.s3.postp = body_postp

    output = shn_rest_controller(module, "body",
                                 main="pr_pe_label",
                                 extra="opt_pr_gender",
                                 rheader=lambda jr: \
                                         shn_dvi_rheader(jr, tabs=[
                                            (T("Recovery"), ""),
                                            (T("Checklist"), "checklist"),
                                            (T("Tracing"), "presence"),
                                            (T("Images"), "image"),
                                            (T("Identity"), "identification"),
                                            (T("Effects Inventory"), "effects"),
                                            (T("Description"), "pd_general"),
                                            (T("Head"), "pd_head"),
                                            (T("Face"), "pd_face"),
                                            (T("Teeth"), "pd_teeth"),
                                            (T("Body"), "pd_body")
                                         ]),
                                 sticky=True,
                                 listadd=False)
    shn_menu()
    return output

# -----------------------------------------------------------------------------
def download():

    """ Download a file. """

    return response.download(request, db)

# -----------------------------------------------------------------------------
def tooltip():

    """ Ajax tooltips """

    if "formfield" in request.vars:
        response.view = "pr/ajaxtips/%s.html" % request.vars.formfield
    return dict()

#
# -----------------------------------------------------------------------------
