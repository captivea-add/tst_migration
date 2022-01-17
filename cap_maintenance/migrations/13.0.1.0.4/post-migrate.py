# cap_maintenance/migrations/13.0.1.0.4/post-migrate.py
# Part of CAPTIVEA. Odoo 13 EE.
"""
Manage module upgrade up to its 13.0.1.0.4 version.
"""

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
    Update 'cap_maintenance' module to its '13.0.1.0.4' version.
    Post migration part.
    """

    # GET ENV VARIABLE
    env = api.Environment(cr, SUPERUSER_ID, {})

    debug("Resize images of 'attachment.picture' records.")
    for record in env["attachment.picture"].search([]):
        record.picture = record.picture
