from odoo import api, SUPERUSER_ID


def set_up_configuration(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Define default lang
    default_lang = env['ir.default'].search([('field_id', '=', env.ref('base.field_res_partner__lang').id)])
    default_lang.json_value = "\"fr_FR\""

    # Link auto generated partners to their company
    tosa_company_partner_id = env.ref('cap_settings.company_tosa').partner_id
    tosa_company_partner_id.company_id = env.ref('cap_settings.company_tosa')

    traction_company_partner_id = env.ref('cap_settings.company_traction').partner_id
    traction_company_partner_id.company_id = env.ref('cap_settings.company_traction')

    puissance_company_partner_id = env.ref('cap_settings.company_puissance').partner_id
    puissance_company_partner_id.company_id = env.ref('cap_settings.company_puissance')
