# -*- coding: utf-8 -*-
{
    'name': "cap_contacts",

    'summary': """
        Contact module overlay for ABB Intervention project.""",

    'description': """
        Contact module overlay for ABB Intervention project.
        Namely : 
        * display Company field for Admin/Settings group
    """,

    'author': "Captivea",
    'website': "https://www.captivea.com",
    'category': 'Tools',
    'version': '0.1',
    'depends': ['contacts'],
    'data': [
        'views/res_partner.xml',
    ],
}
