# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models, _


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    consignment_id = fields.Many2one("maintenance.consignment",string="Consignment")

    @api.model
    def write(self,vals):
        self.ensure_one()
        res = super(SurveyUserInput,self).write(vals)

        if vals.get('state') and vals['state'] == 'done':
            self.consignment_id.generate_pdf()
        return res