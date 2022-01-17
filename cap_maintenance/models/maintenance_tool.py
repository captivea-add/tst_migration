from odoo import models, fields, api


class MaintenanceTool(models.Model):
    _name = 'maintenance.tool'
    _description = 'Maintenance Tool'

    # Lien avec la demande de maintenance (pour l'onglet outillage)
    tools_maintenance_request_id = fields.Many2one(comodel_name='maintenance.request')
    # Lien avec la demande de maintenance (pour l'onglet pièces de rechange)
    spare_parts_maintenance_request_id = fields.Many2one(comodel_name='maintenance.request')

    # Nom
    name = fields.Char(string='Name', translate=True, required=True)
    # Reference (uniquement pour les pièces de rechange)
    reference = fields.Char(string='Reference')
    # Livraison sur site
    is_delivery_on_site = fields.Boolean(string='Delivery On Site')
    # Quantité
    quantity = fields.Float(string='Quantity', required=True)
    # Commentaire
    note = fields.Text(string='Note')
    # Imputation
    assignment = fields.Char(string='Assignement', related='spare_parts_maintenance_request_id.sap_assignment_num')

    # Voyage
    maintenance_travel_id = fields.Many2one(string='Travel', comodel_name='maintenance.travel', required=True)

    # Pièces jointes
    attachment_ids = fields.Many2many(string='File', comodel_name='ir.attachment')
    has_attachment = fields.Boolean(string='Has Attachment', compute='compute_has_attachment')

    def compute_has_attachment(self):
        for record in self:
            record.has_attachment = bool(record.attachment_ids)

    @api.onchange('maintenance_travel_id')
    def onchange_maintenance_travel_id(self):
        maintenance_request_ids = self.env['maintenance.travel']
        if self.get_maintenance_request_id():
            maintenance_request_ids = self.get_maintenance_request_id().maintenance_travel_ids

        domain = [('id', 'in', maintenance_request_ids.ids)]
        return {'domain': {'maintenance_travel_id': domain}}

    def get_maintenance_request_id(self):
        self.ensure_one()
        return self.tools_maintenance_request_id or self.spare_parts_maintenance_request_id

    @api.model
    def create(self, vals):
        tool = super(MaintenanceTool, self).create(vals)

        # Forcer les voyages à être liés à la même demande d'intervention que l'outil
        if tool.maintenance_travel_id and not tool.maintenance_travel_id.maintenance_request_id:
            tool.maintenance_travel_id.maintenance_request_id = tool.get_maintenance_request_id()

        return tool

    def find_all_tools_by_request_and_travel(self, maintenance_request_id, maintenance_travel_id):
        request_domain = [('tools_maintenance_request_id', '=', maintenance_request_id.id)]
        travel_domain = [('maintenance_travel_id', '=', maintenance_travel_id.id)]
        return self.search(request_domain + travel_domain)

    def find_all_spare_part_by_request_and_travel(self, maintenance_request_id, maintenance_travel_id):
        request_domain = [('spare_parts_maintenance_request_id', '=', maintenance_request_id.id)]
        travel_domain = [('maintenance_travel_id', '=', maintenance_travel_id.id)]
        return self.search(request_domain + travel_domain)
