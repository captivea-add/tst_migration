# -*- coding: utf-8 -*-
{
    'name': "cap_survey_report",

    'summary': """
        PDF Generation for Survey Result""",

    'description': """
        PDF Generation for Survey Result
    """,

    'author': "Captivea",
    'website': "https://www.captivea.com",
    'category': 'Operations',
    'version': '0.1',
    'depends': ['survey'],
    'data': [
        'report/report_survey.xml',
        'views/survey_result.xml',
        'views/survey_templates.xml',
        'views/survey_views.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}
