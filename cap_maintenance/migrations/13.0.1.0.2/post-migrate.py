import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, _version):
    """
        Update 'cap_maintenance' module up to its '13.0.1.0.2' version.

        Force active=False on ir.rule with no_update=True
    """

    env = api.Environment(cr, SUPERUSER_ID, {})

    survey_rule = env.ref('survey.survey_user_input_rule_survey_user_cw')
    survey_rule.active = False

    _logger.info("Rule survey.survey_user_input_rule_survey_user_cw archived.")

