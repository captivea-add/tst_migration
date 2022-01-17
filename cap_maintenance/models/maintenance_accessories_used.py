
from odoo import models, fields


class CorrectiveWorkDone(models.Model):
    _name = 'maintenance.accessories.used'
    _description = 'Maintenance Accessories Used'

    maintenance_detailed_report_work_done_id = fields.Many2one(comodel_name='maintenance.detailed.report.work.done')

    # Accessoire
    accessory = fields.Char(string='Accessory', required=True)
    # Ancien numéro de série
    old_serial_no = fields.Char(string='Old Serial Number', required=True)
    # Nouveau numéro de série
    new_serial_no = fields.Char(string='New Serial Number', required=True)
    # Remarque
    note = fields.Html(string='Note')
