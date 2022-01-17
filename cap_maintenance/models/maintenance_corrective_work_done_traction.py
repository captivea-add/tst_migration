
from odoo import models, fields, api, _


class CorrectiveWorkDone(models.Model):
    _name = 'maintenance.corrective.work.done.traction'
    _description = 'Maintenance Corrective Work Done Traction'

    traction_maintenance_detailed_report_work_done_id = fields.Many2one(comodel_name='maintenance.detailed.report.work.done')

    name = fields.Char(compute='compute_name')
    date = fields.Datetime(string='Date')
    worker_id = fields.Many2one(string='Performed By', comodel_name='res.partner', default=lambda self: self.env.user.partner_id)
    corrective_work_done = fields.Html(string='Corrective Work Done')

    def compute_name(self):
        for record in self:
            record.name = str(record.worker_id.name) + " - " + str(record.date)
