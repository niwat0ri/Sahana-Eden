# -*- coding: utf-8 -*-

"""
    Inventory 
    
    @author: Michael Howden (michael@aidiq.com)
    @date-created: 2010-08-16    
    
    A module to record inventories of items at a location
"""

module = request.controller

response.menu_options = inventory_menu

#==============================================================================
def shn_location_rheader(r, tabs=[]):
    if r.representation == "html":
        rheader_tabs = shn_rheader_tabs(r, tabs)
        inventory_location = r.record
        rheader = DIV(TABLE(TR(
                               TH(Tstr("Location") + ": "), shn_gis_location_represent(inventory_location.location_id),
                               TH(Tstr("Description") + ": "), inventory_location.comments,
                               ),
                           ),
                      rheader_tabs
                      )
        return rheader
    return None

def location():
    "RESTful CRUD controller"
    resource = request.function
    tablename = "%s_%s" % (module, resource)
    table = db[tablename]
    
    def postp(jr, output):                          
        shn_action_buttons(jr)
        return output
    response.s3.postp = postp

    rheader = lambda r: shn_location_rheader(r,
                                              tabs = [(T("Details"), None),
                                                      (T("Items"), "location_item"),                                                                                                        
                                                     ]
                                              )

    return shn_rest_controller(module, resource, rheader=rheader, sticky=True)

def index():

    """ Default to the inventory_location list view - TODO does not work with paginate!!!"""

    request.function = "location"
    request.args = []
    return location()
    #module_name = deployment_settings.modules[module].name_nice
    #return dict(module_name=module_name)

#==============================================================================
def location_item():

    """ RESTful CRUD controller """

    resource = request.function
    tablename = "%s_%s" % (module, resource)
    table = db[tablename]
       
    def postp(jr, output):                          
        shn_action_buttons(jr)
        return output
    response.s3.postp = postp    
    
    return shn_rest_controller(module, resource)