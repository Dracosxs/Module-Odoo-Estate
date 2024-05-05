{
    "name": "Estate ",  # The name that will appear in the App list
    "version": "16.0.0",  # Version
    "application": True,  # This line says the module is an App, and not a module
    "depends": [
        "base"
    ],  # dependencies

    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_offer_view.xml',
        'views/estate_property_tags_view.xml',
        'views/estate_property_type_view.xml',
        'views/estate_property_view.xml',
        'views/estate_property_view_users.xml',
        'views/estate_menus.xml'
    ],

    "installable": True,
    'license': 'LGPL-3',

}
