from odoo import models, fields


class MaintenanceStage(models.Model):
    _inherit = 'maintenance.stage'

    active = fields.Boolean(default=True)
