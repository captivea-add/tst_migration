# -*- coding: utf-8 -*-
{
    'name': "cap_settings",

    'summary': """
        Defines global settings for ABB Intervention project.""",

    'description': """
        Defines global settings for ABB Intervention project.
        Namely : 
        * define companies
        * load languages
        * set up admin user
    """,

    'author': "Captivea",
    'website': "https://www.captivea.com",
    'category': 'Tools',
    'version': '1.0.0',
    'depends': ['base', 'mail', 'mail_bot'],
    'data': [
        'data/res_lang.xml',
        'data/res_company.xml',
        'data/res_partner.xml',
        'data/res_users.xml',
    ],
    'post_init_hook': 'set_up_configuration',
}
