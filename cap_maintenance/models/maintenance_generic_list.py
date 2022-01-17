from odoo import models, fields


class MaintenanceGenericList(models.Model):
    _name = 'maintenance.generic.list'
    _description = 'Maintenance List Of Values'

    name = fields.Char(string='Name', translate=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, index=True)

    type = fields.Selection([
        ('uom', "Unit Of Measure"),
        ('flaw_origin', "Flaw Origin"),
    ])
