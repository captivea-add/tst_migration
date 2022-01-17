from odoo import models, fields


class MaintenanceEquipementCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    # Puissance
    puissance_puissance = fields.Integer(string='Power')
    # Unité de puissance
    puissance_puissance_unit = fields.Many2one(string='Unit', comodel_name='maintenance.generic.list', domain=[('type', '=', 'uom')])
    # Tension
    puissance_voltage = fields.Integer(string='Voltage')
    # Type
    puissance_type = fields.Char(string='Type')
    # Type transfo
    puissance_transfo_type = fields.Char(string='Transfo. Type')

    company_type = fields.Selection([('TOSA', 'Related to TOSA'),
                                     ('OTHER', 'Related to Puissance')],
                                    string="Company Type", related='company_id.company_type')