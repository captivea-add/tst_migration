from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    maintenance_request_sequence_id = fields.Many2one(string='Maintenance Request Sequence',
                                                      comodel_name='ir.sequence',
                                                      help='Sequence used for maintenance request numerotation')

    mailing_list_preparation_partner_ids = fields.Many2many(string='Mailing List Preparation',
                                                            comodel_name='res.partner',
                                                            relation='res_company_res_partner_mailing_list_preparation_partner_ids',
                                                            ondelete='restrict',
                                                            check_company=True)
    mailing_list_work_report_partner_ids = fields.Many2many(string='Mailing List Customer Timesheet',
                                                            comodel_name='res.partner',
                                                            relation='res_company_res_partner_mailing_list_work_report_partner_ids',
                                                            ondelete='restrict',
                                                            check_company=True)
    mailing_list_payment_partner_ids = fields.Many2many(string='Mailing List Internal Timesheet',
                                                        comodel_name='res.partner',
                                                        relation='res_company_res_partner_mailing_list_payment_partner_ids',
                                                        ondelete='restrict',
                                                        check_company=True)
