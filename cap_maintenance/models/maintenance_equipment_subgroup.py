from odoo import models, fields


class MaintenanceEquipmentSubgroup(models.Model):
    """
        Caractérise un sous-ensemble d'équipements
    """
    _name = 'maintenance.equipment.subgroup'
    _description = 'Maintenance Equipment Subgroup'

    name = fields.Char(string='Name', translate=True)
    company_id = fields.Many2one(comodel_name='res.company', default=lambda self: self.env.company, index=True, readonly=True)
    equipment_group_id = fields.Many2one(comodel_name='maintenance.equipment.group', required=True, check_company=True)
