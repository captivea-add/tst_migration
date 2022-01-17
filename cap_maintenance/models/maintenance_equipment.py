from odoo import models, fields


class MaintenanceEquipment(models.Model):
    _name = 'maintenance.equipment'
    _inherit = ['maintenance.equipment', 'model.several.copy']

    # Désignation client Tosa
    tosa_customer_code = fields.Char(string='Customer Code TOSA')
    # Date fin garantie Tosa
    tosa_warranty_end_date = fields.Date(string='Warranty End Date')

    # Puissance
    puissance_puissance = fields.Integer(related='category_id.puissance_puissance')
    # Unité de puissance
    puissance_puissance_unit = fields.Many2one(comodel_name='maintenance.generic.list', related='category_id.puissance_puissance_unit')
    # Tension
    puissance_voltage = fields.Integer(related='category_id.puissance_voltage')
    # Type
    puissance_type = fields.Char(related='category_id.puissance_type')

    # Durée garantie
    puissance_warranty_duration = fields.Char(string='Warranty Duration')
    # N° Projet SAP
    puissance_sap_project_num = fields.Char(string='SAP Project N°')
    # Conception SAP
    puissance_sap_design = fields.Char(string='SAP Design')
    # N° Commande
    puissance_order_num = fields.Char(string='Order N°')
    # Type transfo
    puissance_transfo_type = fields.Char(related='category_id.puissance_transfo_type')
    # CdP
    puissance_project_manager = fields.Char(string='Project Manager')

    # Année de fabrication
    commissioning_year = fields.Integer(string='Manufacturing Year')

    company_type = fields.Selection([('TOSA', 'Related to TOSA'),
                                     ('OTHER', 'Related to Puissance')],
                                    string="Company Type", related='company_id.company_type')

