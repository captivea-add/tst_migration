from odoo import models, fields


class MaintenanceRequestType(models.Model):
    """
        Définit le type de maintenance pour ABB.
        Ce type de maintenance diffère du champ standard maintenance_type (correction / préventive)
    """
    _name = 'maintenance.request.type'
    _description = 'Maintenance Request Type'

    name = fields.Char(string='Name', translate=True)
