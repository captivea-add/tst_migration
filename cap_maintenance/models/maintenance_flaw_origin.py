# Part of CAPTIVEA. Odoo 13 EE.

from odoo import fields, models


class MaintenanceFlawOrigin(models.Model):
    """"""

    _name = "maintenance.flaw.origin"
    _description = _name

    ################
    # DISPLAY NAME #
    ################

    name = fields.Char(string="Name", required=True, translate=True)

    ###########
    # COMPANY #
    ###########

    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=lambda self: self.env.company)
