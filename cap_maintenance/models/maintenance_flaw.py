# Part of CAPTIVEA. Odoo 13 EE.

from odoo import models, fields


class MaintenanceFlaw(models.Model):
    """Manage 'maintenance.flaw' model."""

    _name = "maintenance.flaw"
    _description = _name

    ################
    # DISPLAY NAME #
    ################

    name = fields.Char(string="Name", translate=True)

    ###########
    # COMPANY #
    ###########

    company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                 required=True, default=lambda self: self.env.company)
