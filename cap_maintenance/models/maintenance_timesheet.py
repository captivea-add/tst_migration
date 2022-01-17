# cap_maintenance/models/maintenance_timesheet.py
# Part of CAPTIVEA. Odoo 13 EE.
""""""

import base64

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import GettextAlias
import datetime

from ..controllers.main import ReportController

_ = GettextAlias()


# OVERRIDING MODEL
class MaintenanceTimesheet(models.Model):
    """
    Manage 'maintenance.timesheet' model.
    Overriding model.
    """

    _name = 'maintenance.timesheet'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Maintenance Timesheet'

    name = fields.Char(compute='compute_name')

    current_user_id = fields.Many2one(comodel_name='res.users', compute='_compute_current_user_id')

    # Période
    start_date = fields.Date(string='Start date', required=True)
    end_date = fields.Date(string='End date', required=True)

    maintenance_request_id = fields.Many2one(comodel_name='maintenance.request')
    internal_maintenance_request_id = fields.Many2one(comodel_name='maintenance.request')
    # Remarques et photos prises sur site avant et après intervention
    timesheet_type = fields.Selection([('internal', 'Internal'), ('customer', 'Customer')], default='internal')
    # Before work photos
    before_work_attachment_ids = fields.One2many(comodel_name='attachment.picture', string='Before Work Photos',
                                                 inverse_name='customer_timesheet_before_work_attachment_ids',
                                                 help='Get you photos before working and select them here.',)
    # Remarques
    comments = fields.Html()
    # After work photos
    # after_work_attachment_ids = fields.Many2many('ir.attachment', string='After Work Photos',
    #                                              help='Get you photos after working and select them here.',
    #                                              relation='maintenance_timesheet_after_work_attachment_rel')
    after_work_attachment_ids = fields.One2many(comodel_name='attachment.picture', string='After Work Photos',
                                                inverse_name='customer_timesheet_after_work_attachment_ids',
                                                help='Get you photos after working and select them here.',)
    # Intervenant ABB / Intervenant sur site
    worker_id = fields.Many2one(string='Worker', comodel_name='res.partner',
                                default=lambda self: self.env.user.partner_id
                                if self.env.user != self.env.ref('cap_settings.user_generic') else False)
    manager_id = fields.Many2one(string='Manager', comodel_name='res.users', compute='compute_manager_id')

    ######################
    # CUSTOMER SIGNATURE #
    ######################

    # Client non présent
    customer_missing = fields.Boolean(string='Customer is missing', default=False)
    customer_display_name = fields.Char(string='Customer Name')

    # Signature client
    customer_signature = fields.Binary(string='Customer Signature')

    ####################
    # WORKER SIGNATURE #
    ####################

    # Signature Intervenant ABB / Signature intervenant sur site
    worker_signature = fields.Binary(string='Worker Signature')

    ########################
    # SUPERVISOR SIGNATURE #
    ########################

    supervisor_signature = fields.Binary(string="Supervisor Signature")

    set_supervisor_signature_readonly = fields.Boolean(string="Set The 'Supervisor Signature' Field Readonly ?",
                                                       compute="compute_set_supervisor_signature_readonly",
                                                       search="search_set_supervisor_signature_readonly")

    def round_time(self, field):
        hours = filter(lambda x: x > 0, self.timesheet_line_ids.mapped(field))
        time_hours = []
        for hour in hours:
            time_hours.append('{0:02.0f}:{1:02.0f}'.format(*divmod(float(hour) * 60, 60)))
        mysum = datetime.timedelta()
        for i in time_hours:
            (h, m) = i.split(':')
            d = datetime.timedelta(hours=int(h), minutes=int(m))
            mysum += d
        totsec = mysum.total_seconds()
        h = totsec // 3600
        m = (totsec % 3600) // 60
        sec = (totsec % 3600) % 60  # just for reference

        return "%d:%d" % (h, m)

    @api.depends("manager_id")
    def compute_set_supervisor_signature_readonly(self):
        """
        Compute the 'set_supervisor_signature_readonly' field value of some 'maintenance.timesheet'.

        Supervisor signature must be readonly when:
        - current user is not the maintenance request manager
        """
        for record in self:
            value = False
            if self.env.user != record.manager_id:
                value = True
            record.set_supervisor_signature_readonly = value

    def search_set_supervisor_signature_readonly(self, operator, value):
        """
        Filter 'maintenance.timesheet' records based on the 'set_supervisor_signature_readonly' field value.

        The concerned field is a boolean field.
        So, we have to consider:
        - the 'field is value' case when operator is '=',
        - the 'field is not value' case when operator is '!='.
        """
        # PREPARE
        field = "set_supervisor_signature_readonly"
        records = self.env[self._name].search([])
        # BOOLEAN FIELD IS VALUE
        if operator == "=":
            records = records.filtered(lambda record: record[field] is value)
        # BOOLEAN FIELD IS NOT VALUE
        elif operator == "!=":
            records = records.filtered(lambda record: record[field] is not value)
        # RETURN DOMAIN TO USE
        return [("id", "in", records.ids)]

    ####
    #  #
    ####

    # Modalité compensation heures supplémentaires
    extra_hours_management_values = [('to_pay', 'To Pay'), ('to_compensate', 'To Compensate')]
    extra_hours_management = fields.Selection(selection=extra_hours_management_values, string='Extra Hours')
    # Lignes de feuille de temps
    timesheet_line_ids = fields.One2many(comodel_name='maintenance.timesheet.line',
                                         inverse_name='maintenance_timesheet_id', string='Logged Hours',
                                         default=lambda self: self.default_timesheet_line_ids())

    # Est signé
    is_signed = fields.Boolean(string='Is signed', compute='compute_is_signed', store=True)
    # Total des heures sur la période
    total_hours = fields.Integer(string='Total Hours', compute='compute_total_hours')
    # Total des kilomètres sur la période
    total_kms = fields.Integer(string='Total Kms', compute='compute_total_kms')
    # Indemnité kilométrique
    allowance_per_km = fields.Monetary(string='Allowance Per Km', currency_field='chf_currency_id')

    # Montant du déplacement
    allowance_total_kms_amount = fields.Monetary(string='Amount', currency_field='chf_currency_id',
                                                 compute='compute_allowance_total_kms_amount')
    # Feuille diffusée
    is_email_sent = fields.Boolean(string='Email sent', readonly=True, store=True)

    chf_currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.ref('base.CHF'))

    # Repas de midi
    lunch_allowance_currency_id = fields.Many2one('res.currency', string='Currency',
                                                  default=lambda self: self.env.company.currency_id)
    lunch_allowance_days = fields.Integer(string='# Days')
    lunch_allowance_amount = fields.Monetary(string='Amount/Day', currency_field='lunch_allowance_currency_id')
    lunch_allowance_total_amount = fields.Monetary(string='Total', compute='compute_lunch_allowance_total_amount',
                                                   currency_field='lunch_allowance_currency_id')
    # Repas du soir
    diner_allowance_currency_id = fields.Many2one('res.currency', string='Currency',
                                                  default=lambda self: self.env.company.currency_id)
    diner_allowance_days = fields.Integer(string='# Days')
    diner_allowance_amount = fields.Monetary(string='Amount/Day', currency_field='diner_allowance_currency_id')
    diner_allowance_total_amount = fields.Monetary(string='Total', compute='compute_diner_allowance_total_amount',
                                                   currency_field='diner_allowance_currency_id')
    # Nuitée
    night_allowance_currency_id = fields.Many2one('res.currency', string='Currency',
                                                  default=lambda self: self.env.company.currency_id)
    night_allowance_days = fields.Integer(string='# Days')
    night_allowance_amount = fields.Monetary(string='Amount/Day', currency_field='night_allowance_currency_id')
    night_allowance_total_amount = fields.Monetary(string='Total', compute='compute_night_allowance_total_amount',
                                                   currency_field='night_allowance_currency_id')
    # Primes de travaux difficiles
    hard_work_bonus_days = fields.Integer(string='# Days')
    hard_work_bonus_amount = fields.Monetary(string='Amount/Day', currency_field='chf_currency_id')
    hard_work_bonus_total_amount = fields.Monetary(string='Total', compute='compute_hard_work_bonus_total_amount',
                                                   currency_field='chf_currency_id')
    # Supplément par pays
    other_country_bonus_days = fields.Integer(string='# Days')
    other_country_bonus_amount = fields.Monetary(string='Amount/Day', currency_field='chf_currency_id')
    other_country_bonus_total_amount = fields.Monetary(string='Total',
                                                       compute='compute_other_country_bonus_total_amount',
                                                       currency_field='chf_currency_id')

    # Expenses
    maintenance_expense_ids = fields.One2many(string='Expenses', comodel_name='maintenance.expense',
                                              inverse_name='maintenance_timesheet_id')
    expenses_count = fields.Integer(String='Registered Expenses', compute='compute_expenses_count')

    is_locked = fields.Boolean(compute='compute_is_locked', store=True)

    # -------------------------------------------------------------------------------------------
    #                                   CALCULATED FIELDS
    # -------------------------------------------------------------------------------------------

    def _compute_current_user_id(self):
        for record in self:
            record.current_user_id = self.env.user

    @api.depends('timesheet_type', 'is_signed', 'is_email_sent')
    def compute_is_locked(self):
        for record in self:
            is_locked = False
            if record.id:
                if record.timesheet_type == 'customer' and record.is_signed:
                    is_locked = True
            record.is_locked = is_locked

    @api.onchange('total_kms', 'allowance_per_km')
    def compute_allowance_total_kms_amount(self):
        for record in self:
            record.allowance_total_kms_amount = record.allowance_per_km * record.total_kms

    def compute_manager_id(self):
        for record in self:
            request_id = record.maintenance_request_id or record.internal_maintenance_request_id
            record.manager_id = request_id.manager_id

    @api.depends('maintenance_expense_ids')
    def compute_expenses_count(self):
        for record in self:
            record.expenses_count = len(record.maintenance_expense_ids)

    @api.depends('lunch_allowance_days', 'lunch_allowance_amount')
    def compute_lunch_allowance_total_amount(self):
        for record in self:
            record.lunch_allowance_total_amount = record.lunch_allowance_days * record.lunch_allowance_amount

    @api.depends('diner_allowance_days', 'diner_allowance_amount')
    def compute_diner_allowance_total_amount(self):
        for record in self:
            record.diner_allowance_total_amount = record.diner_allowance_days * record.diner_allowance_amount

    @api.depends('night_allowance_days', 'night_allowance_amount')
    def compute_night_allowance_total_amount(self):
        for record in self:
            record.night_allowance_total_amount = record.night_allowance_days * record.night_allowance_amount

    @api.depends('hard_work_bonus_days', 'hard_work_bonus_amount')
    def compute_hard_work_bonus_total_amount(self):
        for record in self:
            record.hard_work_bonus_total_amount = record.hard_work_bonus_days * record.hard_work_bonus_amount

    @api.depends('other_country_bonus_days', 'other_country_bonus_amount')
    def compute_other_country_bonus_total_amount(self):
        for record in self:
            record.other_country_bonus_total_amount = record.other_country_bonus_days \
                                                      * record.other_country_bonus_amount

    @api.depends('customer_signature',)
    def compute_is_signed(self):
        for record in self:
            record.is_signed = record.customer_signature

    def default_timesheet_line_ids(self):
        _timesheet_line_ids = []
        for i in range(31):
            _timesheet_line_ids.append({
                'maintenance_timesheet_id': self.id,
                'sequence': i + 1,
            })
        return _timesheet_line_ids

    @api.depends('timesheet_line_ids')
    def compute_total_hours(self):
        for record in self:
            record.total_hours = sum(record.timesheet_line_ids.mapped('total_hours'))

    @api.depends('timesheet_line_ids')
    def compute_total_kms(self):
        for record in self:
            record.total_kms = sum(record.timesheet_line_ids.mapped('kilometers'))

    def compute_name(self):
        for record in self:
            record.name = "".join([str(record.worker_id.name), " [",
                                   str(record.start_date), " - ",
                                   str(record.end_date), "]"])

    def action_preview_pdf(self):
        """ Manage View PDF action """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': ReportController.get_print_to_pdf_url(self),
            'target': 'new',
        }

    def action_send_administrative_mail(self):
        """
            Send timesheet to administrative team
        """
        need_signature = self.filtered(lambda r: not bool(r.worker_signature))
        if need_signature:
            raise UserError(_("Don't forget to sign it before sending it."))

        for record in self:
            if record.timesheet_type == 'customer':
                template = self.env.ref('cap_maintenance.customer_maintenance_timesheet_mail_template')
                message_id = template.sudo().send_mail(record.id)
                mail_id = self.env['mail.mail'].sudo().browse([message_id])
                # Force administrative team as recipient
                mail_id.email_to = ",".join(self.env.company.mailing_list_work_report_partner_ids.mapped('email'))
                mail_id.attachment_ids = record.sudo().create_report_attachment()
                record.sudo().message_post(subject=_("Administrative Team Notification"), body=_("Timesheet sent to administrative team"), attachment_ids=mail_id.attachment_ids.ids)
                mail_id.send()

            if record.timesheet_type == 'internal':
                template = self.env.ref('cap_maintenance.internal_maintenance_timesheet_mail_template')
                domain = [('res_model', '=', 'maintenance.expense'),
                          ('res_field', '=', 'attachment'),
                          ('res_id', 'in', record.maintenance_expense_ids.ids)]
                attachment_ids = self.env['ir.attachment'].sudo().search(domain)
                attachment_ids += record.sudo().create_report_attachment()
                message_id = template.sudo().send_mail(record.id)
                mail_id = self.env['mail.mail'].sudo().browse([message_id])
                # Force administrative team as recipient
                mail_id.email_to = ",".join(self.env.company.mailing_list_payment_partner_ids.mapped('email'))
                mail_id.attachment_ids = attachment_ids
                record.sudo().message_post(subject=_("Administrative Team Notification"), body=_("Timesheet sent to administrative team"), attachment_ids=mail_id.attachment_ids.ids)
                mail_id.send()

    def action_send_mail(self):
        """ Send timesheet to customer or support """
        need_signature = self.filtered(lambda r: not bool(r.worker_signature))
        if need_signature:
            raise UserError(_("Don't forget to sign it before sending it."))

        for record in self:
            if record.timesheet_type == 'internal':
                if not record.internal_maintenance_request_id.mailing_list_payment_partner_ids:
                    raise UserError(_("Please fill 'Mailing List Spent Hours' field first."))
                record.internal_maintenance_request_id.mailing_list_payment_partner_ids.raise_if_missing_email()
            else:
                if not record.maintenance_request_id.mailing_list_work_report_partner_ids:
                    raise UserError(_("Please fill 'Mailing List Customer Timesheet' field first."))
                record.maintenance_request_id.mailing_list_work_report_partner_ids.raise_if_missing_email()
                # Empêcher l'envoi d'email si Take 5 / Déconsignation / Consignation n'est pas renseigné
                record.maintenance_request_id.raise_if_missing_form()

        for record in self:
            if record.timesheet_type == 'customer':
                template = self.env.ref('cap_maintenance.customer_maintenance_timesheet_mail_template')
                message_id = template.send_mail(record.id)
                mail_id = self.env['mail.mail'].browse([message_id])
                mail_id.email_to = ",".join(record.maintenance_request_id.
                                            mailing_list_payment_partner_ids.mapped('email'))
                mail_id.attachment_ids = record.create_report_attachment()
                record.message_post(subject=mail_id.subject, body=mail_id.body_html,
                                    attachment_ids=mail_id.attachment_ids.ids)
                mail_id.send()

            if record.timesheet_type == 'internal':
                template = self.env.ref('cap_maintenance.internal_maintenance_timesheet_mail_template')
                domain = [('res_model', '=', 'maintenance.expense'),
                          ('res_field', '=', 'attachment'),
                          ('res_id', 'in', record.maintenance_expense_ids.ids)]
                attachment_ids = self.env['ir.attachment'].search(domain)
                attachment_ids += record.create_report_attachment()
                message_id = template.send_mail(record.id)
                mail_id = self.env['mail.mail'].browse([message_id])
                mail_id.email_to = ",".join(record.internal_maintenance_request_id.
                                            mailing_list_payment_partner_ids.mapped('email'))
                mail_id.attachment_ids = attachment_ids
                record.message_post(subject=mail_id.subject, body=mail_id.body_html,
                                    attachment_ids=mail_id.attachment_ids.ids)
                mail_id.send()

            if not record.is_email_sent:
                record.is_email_sent = True

    def build_report_name(self):
        maintenance_request_id = self.internal_maintenance_request_id or self.maintenance_request_id
        equipment = maintenance_request_id.equipment_id.name if maintenance_request_id.equipment_id else ''
        request_num = maintenance_request_id.company_request_num
        timesheet_type = _("Internal Timesheet")
        if self.timesheet_type == "customer":
            timesheet_type = _("Customer Timesheet")
        report_name = _('Equipment[{equipment}] Intervention[{request_num}] {timesheet_type}')
        report_name = report_name.format(equipment=equipment, request_num=request_num, timesheet_type=timesheet_type)
        return report_name

    def create_report_attachment(self):
        self.ensure_one()
        filename = self.build_report_name()
        pdf = self.build_report_as_pdf()
        attachment = self.env['ir.attachment'].sudo().create({
            'name': filename + '.pdf',
            'datas': base64.b64encode(pdf),
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })
        return attachment

    def build_report_as_pdf(self):
        """ Generate PDF report """
        self.ensure_one()
        pdf = self.env.ref('cap_maintenance.action_print_maintenance_timesheet_report'). \
            render_qweb_pdf(res_ids=[self.id])[0]
        return pdf

    def write(self, vals):
        return super(MaintenanceTimesheet, self).write(vals)

    def unlink(self):
        """ Make sure it's not possible to delete neither a signed customer timesheet
        nor an internal sent timesheet"""
        self.check_locked()
        return super(MaintenanceTimesheet, self).unlink()

    def check_locked(self):
        for record in self:
            if record.timesheet_type == 'customer' and record.is_locked:
                raise UserError(_('You cannot update nor delete signed timesheet.'))
            if record.timesheet_type == 'internal' and record.is_locked:
                raise UserError(_('You cannot update nor delete a timesheet which has already been sent.'))

    @api.constrains('schedule_date', 'end_date')
    def _check_working_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError(_('End date must be greater than Start Date.'))
