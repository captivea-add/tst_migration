# Part of CAPTIVEA. Odoo 12 EE.

import logging

# from odoo import api, SUPERUSER_ID

_logger = logging.getLogger("odoo.modules.migration")
_module_name = "module cap_maintenance:"


def debug(message):
    """Log a DEBUG message with correct prefix and logger."""
    message = "{} " + message
    message = message.format(_module_name)
    _logger.debug(message)


def migrate(cr, _version):
    """Update 'cap_maintenance' module up to its '13.0.1.0.1' version. Pre migration part."""

    # GET ENV VARIABLE
    # env = api.Environment(cr, SUPERUSER_ID, {})

    debug("Empty old 'major_flaw' field of 'maintenance.request' records.")

    cr.execute("UPDATE maintenance_request SET major_flaw=NULL")
