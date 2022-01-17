# -*- coding: utf-8 -*-
import json

from odoo import http
from odoo.http import request
from odoo.addons.survey.controllers.main import Survey
from odoo import SUPERUSER_ID


class Survey(Survey):

    @http.route(['/survey/cprefill/<string:survey_token>/<string:answer_token>',
                 '/survey/cprefill/<string:survey_token>/<string:answer_token>/<model("survey.page"):page>'],
                type='http', auth='public', website=True)
    def custom_prefill(self, survey_token, answer_token, page=None, **post):
        UserInputLine = request.env['survey.user_input_line']
        ret = {}

        survey = request.env['survey.survey'].with_context(active_test=False).sudo().search([('access_token', '=', survey_token)])

        # Fetch previous answers
        if page:
            domain = [('user_input_id.token', '=', answer_token), ('page_id', '=', page.id)]
        else:
            domain = [('user_input_id.token', '=', answer_token)]

        # Return non empty answers in a JSON compatible format
        previous_answers = UserInputLine.with_user(request.env['res.users'].browse(SUPERUSER_ID)).search(domain)
        for answer in previous_answers:
            if not answer.skipped:
                answer_data = answer.read()[0]
                answer_tag = '%s_%s' % (answer.survey_id.id, answer.question_id.id)
                if answer.answer_type == 'sign':
                    answer_value = answer.img_sign
                    ret.update({answer_tag: answer_value.decode('utf-8')})
                elif answer.answer_type == 'attachment':
                    answer_value = answer.attachment_id.datas
                    ret.update({answer_tag: answer_value.decode('utf-8')})
        return json.dumps(ret)
