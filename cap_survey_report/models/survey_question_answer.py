from odoo import models, fields
from odoo.tools import OrderedSet


class SurveyQuestionAnswer(models.TransientModel):
    _name = 'survey.question.answer'
    _description = 'Survey Question Answer'

    response_id = fields.Many2one(comodel_name='survey.user_input')

    survey_id = fields.Many2one(comodel_name='survey.survey', related='response_id.survey_id')

    question_id = fields.Many2one(comodel_name='survey.question')

    user_input_line_ids = fields.Many2many(comodel_name='survey.user_input_line', compute='compute_user_input_line_ids')

    def get_result_report_data(self, response_id):
        """ Return dict with necessary data for result report generation """
        q_a = self.env[self._name]
        res = {}
        if response_id:
            question_ids = OrderedSet()

            if response_id.user_input_line_ids:
                for user_line in response_id.user_input_line_ids:
                    question_ids.add(user_line.question_id)
            else:
                for question in response_id.survey_id.question_and_page_ids:
                    question_ids.add(question)

            for question_id in question_ids:
                question_answer_id = self.env[self._name].create({
                    'response_id': response_id.id,
                    'question_id': question_id.id
                })
                question_answer_id.compute_user_input_line_ids()
                q_a += question_answer_id

            res = {
                'survey': response_id.survey_id,
                'questions': q_a,
            }

        return res

    def compute_user_input_line_ids(self):
        """
            Identify all answers related to the same question (multiple answers)
        """
        for record in self:
            related_lines_domain = [('question_id', '=', self.question_id.id), ('user_input_id', '=', self.response_id.id)]
            record.user_input_line_ids = self.env['survey.user_input_line'].search(related_lines_domain)

    def get_user_input_line_for(self, label_id):
        user_input_line = self.user_input_line_ids.filtered(lambda line: line.value_suggested == label_id or line.value_suggested_row == label_id)
        return user_input_line

    def get_user_input_line_for_matrix(self, label_id_1, label_id_2):
        user_input_line = self.user_input_line_ids.filtered(lambda line: line.value_suggested == label_id_1 and line.value_suggested_row == label_id_2)
        return user_input_line

    def get_comment(self):
        user_input_line = self.user_input_line_ids.filtered(lambda line: not line.value_suggested and not line.value_suggested_row and line.value_text)
        return user_input_line
