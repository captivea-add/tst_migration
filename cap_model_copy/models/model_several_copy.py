from odoo import models, api, _


class ModelSeveralCopy(models.AbstractModel):
    """
        Provided the ability to duplicate records multiple times at once.
    """
    _name = 'model.several.copy'
    _description = 'Model Copy'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
            Proper way to inject action into every view
        """
        result = super(ModelSeveralCopy, self).fields_view_get(view_id, view_type, toolbar, submenu)
        if toolbar:
            result['toolbar']['action'].append(self.get_action_copy_wizard())

        return result

    def get_action_copy_wizard(self):
        """
            Action to insert in every view in order to access duplication wizard
        """
        action_rec = self.env.ref('cap_model_copy.action_view_wizard_several_copy')
        action = action_rec.read()[0]
        action['context'] = dict(self.env.context)

        return action
