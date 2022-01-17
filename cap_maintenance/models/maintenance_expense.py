from odoo import models, fields


class MaintenanceExpense(models.Model):
    _name = 'maintenance.expense'
    _description = 'Maintenance Expense'

    description = fields.Char(string='Description', required=True)
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id, required=True)

    attachment = fields.Binary(string='Attachment',  help="Upload your bill.", attachment=True)

    maintenance_timesheet_id = fields.Many2one(comodel_name='maintenance.timesheet')
