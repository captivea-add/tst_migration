# Part of CAPTIVEA. Odoo 13 EE.

import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger("odoo.modules.migration")
_module_name = "module cap_maintenance:"


def debug(message):
    """
    Log a DEBUG message with correct prefix and logger.
    """
    message = "{} " + message
    message = message.format(_module_name)
    _logger.debug(message)


def migrate(cr, _version):
    """
    Update 'cap_maintenance' module to its '13.0.1.0.3' version.
    Post migration part.
    """

    # GET ENV VARIABLE
    env = api.Environment(cr, SUPERUSER_ID, {})

    debug("Recompute 'is_signed' field value of existing 'maintenance.detailed.report.work.done' records.")
    env["maintenance.detailed.report.work.done"].search([]).compute_is_signed()

    debug("Recompute 'is_signed' field value of existing 'maintenance.timesheet' records.")
    env["maintenance.timesheet"].search([]).compute_is_signed()
