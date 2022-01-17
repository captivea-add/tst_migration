from odoo import models, fields


class MaintenanceSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mailing_list_preparation_partner_ids = fields.Many2many(string='Mailing List Preparation',
                                                            related='company_id.mailing_list_preparation_partner_ids',
                                                            check_company=True,
                                                            readonly=False)
    mailing_list_work_report_partner_ids = fields.Many2many(string='Mailing List Customer Timesheet',
                                                            related='company_id.mailing_list_work_report_partner_ids',
                                                            check_company=True,
                                                            readonly=False)
    mailing_list_payment_partner_ids = fields.Many2many(string='Mailing List Internal Timesheet',
                                                        related='company_id.mailing_list_payment_partner_ids',
                                                        check_company=True,
                                                        readonly=False)
