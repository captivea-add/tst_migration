from odoo import models, fields, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    matricule = fields.Char(string='Matricule')

    def get_emails(self):
        return str(",".join([str(x.id) for x in self]))

    def raise_if_missing_email(self):
        email_missing_records = self.filtered(lambda r: not r.email)
        if email_missing_records:
            raise UserError(_("{} do not have any email registered.").format(", ".join([r.name for r in email_missing_records])))
