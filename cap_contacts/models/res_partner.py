from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def default_get(self, default_fields):
        """Add the company of the parent as default if we are creating a child partner."""
        values = super().default_get(default_fields)
        if 'parent_id' in default_fields and values.get('parent_id'):
            values['company_id'] = self.browse(values.get('parent_id')).company_id.id

        if 'company_id' not in values:
            values['company_id'] = self.env.company.id

        return values