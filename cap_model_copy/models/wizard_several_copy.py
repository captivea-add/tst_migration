from odoo import models, fields, _
from odoo.exceptions import UserError


class WizardSeveralCopy(models.TransientModel):
    """
        Provide options before copying
    """
    _name = 'wizard.several.copy'
    _description = 'Wizard Several Copies At Once'

    number_of_copy = fields.Integer(string='Additional copies', default=1)

    def copy_several_times(self):
        if self.number_of_copy < 1:
            raise UserError(_("Copying record(s) less than 1 times makes no sens. Please fix it or cancel."))

        context = self.env.context
        model_name = context['active_model']
        record_ids = self.env[model_name].browse(context['active_ids'])

        for record in record_ids:
            for num in range(self.number_of_copy):
                record.copy()
