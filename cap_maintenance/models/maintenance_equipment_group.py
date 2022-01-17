from odoo import models, fields


class MaintenanceEquipmentGroup(models.Model):
    """
        Caractérise un ensemble d'équipements
    """
    _name = 'maintenance.equipment.group'
    _description = 'Maintenance Equipment Group'

    name = fields.Char(string='Name', translate=True)
    company_id = fields.Many2one(comodel_name='res.company', default=lambda self: self.env.company, index=True, readonly=True)
    equipment_subgroup_ids = fields.One2many(comodel_name='maintenance.equipment.subgroup', inverse_name='equipment_group_id', ondelete='restrict', check_company=True)
