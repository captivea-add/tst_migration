# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models, _


class Survey(models.Model):
    _inherit = 'survey.survey'



    @api.model
    def prepare_result(self, question, current_filters=None):
        current_filters = current_filters if current_filters else []

        # Sign
        # Attachment
        if question.question_type in ['sign', 'attachment']:
            result_summary = []
            for input_line in question.user_input_line_ids:
                if not current_filters or input_line.user_input_id.id in current_filters:
                    result_summary.append(input_line)
            return result_summary

        return super(Survey, self).prepare_result(question, current_filters)


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    title = fields.Text('Title', required=True, translate=True)
    question = fields.Text('Question', related="title")
    question_type = fields.Selection(selection_add=[('sign', 'Signature'), ('attachment', 'Attachment')])

    # Validate Fields
    def validate_sign(self, post, answer_tag):
        return self.simple_validation(post, answer_tag)

    def validate_attachment(self, post, answer_tag):
        return self.simple_validation(post, answer_tag)

    def simple_validation(self, post, answer_tag):
        errors = {}
        answer = post.get(answer_tag, '')
        if self.constr_mandatory and not answer:
            errors.update({answer_tag: self.constr_error_msg})
        return errors


class UserInput(models.Model):
    _inherit = 'survey.user_input_line'

    answer_type = fields.Selection(selection_add=[('sign', 'Signature'), ('attachment', 'Attachment')])
    img_sign = fields.Binary("Signature")
    attachment_id = fields.Many2one(string='Attachment', comodel_name='ir.attachment')

    # Save Fields
    @api.model
    def save_line_sign(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'page_id': question.page_id.id,
            'survey_id': question.survey_id.id,
            'skipped': False
        }

        if answer_tag in post and post[answer_tag].strip():
            img_data = post[answer_tag]
            vals.update({'answer_type': 'sign', 'img_sign': img_data})
        else:
            vals.update({'answer_type': None, 'skipped': True})

        old_uil = self.search([('user_input_id', '=', user_input_id), ('survey_id', '=', question.survey_id.id), ('question_id', '=', question.id)])
        if old_uil:
            old_uil.write(vals)
        else:
            old_uil.create(vals)
        return True

    @api.model
    def save_line_attachment(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'page_id': question.page_id.id,
            'answer_type': 'attachment',
            'survey_id': question.survey_id.id,
            'skipped': False
        }

        old_uil = self.search([('user_input_id', '=', user_input_id), ('survey_id', '=', question.survey_id.id), ('question_id', '=', question.id)], limit=1)

        attachment_vals = {}
        attachment = self.env['ir.attachment'].sudo()
        # If user uploaded a file
        if post.get(answer_tag, '') != '':
            file = post[answer_tag]
            attachment_vals.update({
                'name': file.filename,
                'store_fname': file.filename,
                'res_model': self._name,
                'res_id': old_uil.id,
                'datas': base64.b64encode(file.read()),
                'description': question.question,
            })
            # Create attachment if not found
            if not old_uil.attachment_id:
                attachment = attachment.create(attachment_vals)
                vals.update({'attachment_id': attachment.id})
        # User didnt upload any file
        else:
            vals.update({'answer_type': None, 'skipped': True})

        # Survey anwser has been edited
        if old_uil:
            if attachment_vals and old_uil.attachment_id:
                old_uil.attachment_id.write(attachment_vals)
            old_uil.write(vals)
        # First time the question is answered
        else:
            uil = self.create(vals)
            if attachment:
                attachment.write({'res_id': uil.id})
        return True
