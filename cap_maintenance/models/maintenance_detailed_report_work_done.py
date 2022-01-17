import base64

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

from ..controllers.main import ReportController


class DetailedReportWorkDone(models.Model):
    _name = 'maintenance.detailed.report.work.done'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Maintenance Detailed Report Work Done'

    # -------------------------------------------------------------------
    # Champs communs toutes sociétés
    # ------------------------------------------------------------------
    name = fields.Char(compute='compute_name')
    maintenance_request_id = fields.Many2one(comodel_name='maintenance.request')
    company_id = fields.Many2one(string='Company', comodel_name='res.company', related='maintenance_request_id.company_id')
    company_type = fields.Selection([('TOSA', 'Related to TOSA'),
                                     ('OTHER', 'Related to Puissance')],
                                    string="Company Type", related='company_id.company_type')

    report_title = fields.Char(string='Title', translate=True, compute='compute_report_title')
    report_lang = fields.Many2one(string='Report Lang', comodel_name='res.lang', default=lambda self: self.env['res.lang'].search([('code', '=', self.env.lang)], limit=1))
    author = fields.Many2one(string='Author', comodel_name='res.partner', domain=[('matricule', '!=', False)], required=True)

    # Document
    document_num = fields.Char(string='Document')
    # Revision
    document_revision = fields.Char(string='Revision')

    # Signature client
    is_customer_signature_required = fields.Boolean(string="Require Customer Signature")
    customer_signature = fields.Binary(string='Customer Signature')
    # Signature Intervenant ABB / Signature intervenant sur site
    worker_signature = fields.Binary(string='Worker Signature')
    # Remarques
    note = fields.Html(string='Note')
    picture_attachment_ids = fields.One2many(string='Pictures',
                                                 help='Get some pictures and select them here.',
                                                 comodel_name='attachment.picture',
                                                 inverse_name='detailed_report_work_done_ids',
                                                 copy=True)

    # Période
    start_date = fields.Date(string='Start date')
    end_date = fields.Date(string='End date')

    # -------------------------------------------------------------------
    # Champs spécifiques pour la société : Puissance
    # -------------------------------------------------------------------
    work_description = fields.Html(string='Work Description', related='maintenance_request_id.work_comment')
    work_done_description = fields.Html(string='Work Done Description')
    standard_project_photos = fields.Html(string='Standard Project Photos')
    work_done_section_1_image = fields.Binary(string='Photo plaque signalétique transformateur et régleur sous charge')
    work_done_section_1_note = fields.Text(string='Note')
    work_done_section_2_image = fields.Binary(string='Photo des mâts de mise à terre côté BT et HT')
    work_done_section_2_note = fields.Text(string='Note')
    work_done_section_3_image = fields.Binary(string='Photo installation chantier (outillage, citerne, bac rétention etc…)')
    work_done_section_3_note = fields.Text(string='Note')
    work_done_section_4_image = fields.Binary(string='Photo Remplissage transformateur ou régleur sous charge')
    work_done_section_4_note = fields.Text(string='Note')
    work_done_section_5_image = fields.Binary(string='Traitement d’huile du transformateur et niveau d’huile transformateur et régleur')
    work_done_section_5_note = fields.Text(string='Note')
    corrective_work_to_plan = fields.Html(string='Corrective Work To Plan')
    preventive_work_to_plan = fields.Html(string='Preventive Work To Plan')

    # -------------------------------------------------------------------
    # Champs spécifiques pour la société : Traction
    # -------------------------------------------------------------------
    # N° de véhicule
    vehicle_serial = fields.Char(string='Vehicle serial #')
    # Description des travaux
    traction_corrective_work_ids = fields.One2many(comodel_name='maintenance.corrective.work.done.traction', inverse_name='traction_maintenance_detailed_report_work_done_id',copy=True)
    # Constat de fuite d'huile
    is_oil_leakage = fields.Boolean()
    oil_leakage_worker_id = fields.Many2one(comodel_name='res.partner')
    oil_leakage_date = fields.Datetime()
    oil_leakage_location = fields.Text(string='Oil Leakage Location')
    # Accessoires
    accessories_used_ids = fields.One2many(comodel_name='maintenance.accessories.used', inverse_name='maintenance_detailed_report_work_done_id',copy=True)
    # Ajout d'huile
    oil_top_up_quantity = fields.Float()
    oil_top_up_worker_id = fields.Many2one(comodel_name='res.partner')
    oil_top_up_date = fields.Datetime()
    # Dégazage complet
    degassing_worker_id = fields.Many2one(comodel_name='res.partner')
    degassing_date = fields.Datetime()
    # Fonctionnement de la pompe
    pump_check_up_quantity = fields.Float()
    pump_check_up_worker_id = fields.Many2one(comodel_name='res.partner')
    pump_check_up_date = fields.Datetime()
    # Test d'étanchéité
    oil_tightness_check_worker_id = fields.Many2one(comodel_name='res.partner')
    oil_tightness_check_date = fields.Datetime()
    # Durée
    duration = fields.Float()
    duration_worker_id = fields.Many2one(comodel_name='res.partner')
    duration_date = fields.Datetime()
    # Pression
    pressure = fields.Float()
    pressure_worker_id = fields.Many2one(comodel_name='res.partner')
    pressure_date = fields.Datetime()
    # Prise d'échantillon
    oil_sampling_worker_id = fields.Many2one(comodel_name='res.partner')
    oil_sampling_date = fields.Datetime()
    # Travaux terminés
    is_rework_competed = fields.Boolean()
    rework_competed_worker_id = fields.Many2one(comodel_name='res.partner')
    rework_competed_date = fields.Datetime()

    # -------------------------------------------------------------------
    # Champs pour la société : TOSA
    # -------------------------------------------------------------------
    # Nature de l'intervention
    issue_description = fields.Html(string='Issue Description')
    # Activités réalisées
    corrective_work_done = fields.Html(string='Corrective Work Done')
    # Tests de validation réalisées
    validation_work_done = fields.Html(string='Validation Work Done')

    manager_id = fields.Many2one(comodel_name='res.users', related='maintenance_request_id.manager_id')
    # Date du rapport
    report_date = fields.Date(string='Report Date')

    # Est signé
    is_signed = fields.Boolean(string='Is signed', compute='compute_is_signed', store=True)

    def compute_report_title(self):
        for record in self:
            if record.company_id == self.env.ref('cap_settings.company_tosa'):
                record.report_title = _('Intervention Report')
            elif record.company_id == self.env.ref('cap_settings.company_traction'):
                record.report_title = _('Work and Instruction Report')
            elif record.company_id == self.env.ref('cap_settings.company_puissance'):
                record.report_title = _('Intervention Report')

    @api.depends('customer_signature', 'is_customer_signature_required')
    def compute_is_signed(self):
        for record in self:
            if record.id:
                record.is_signed = record.customer_signature and record.is_customer_signature_required

    @api.constrains('start_date', 'end_date')
    def _check_working_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError(_('End date must be greater than Start Date.'))

    def compute_name(self):
        for record in self:
            record.name = _("Report")

    def action_send_mail(self):
        # Empêcher l’envoi de l’email si Take 5 / Déconsignation / Consignation n'est pas renseigné
        self.mapped('maintenance_request_id').raise_if_missing_form()

        is_recipient_missing = self.filtered(lambda r: not r.maintenance_request_id.mailing_list_final_report_partner_ids)
        if is_recipient_missing:
            raise UserError(_("Please fill 'Mailing List Final Report' field first."))

        self.maintenance_request_id.mailing_list_final_report_partner_ids.raise_if_missing_email()

        for record in self:
            template = self.env.ref('cap_maintenance.detailed_report_work_done_mail_template')
            message_id = template.send_mail(record.id)
            mail_id = self.env['mail.mail'].browse([message_id])
            mail_id.attachment_ids = record.create_report_attachment()
            record.message_post(subject=mail_id.subject, body=mail_id.body_html, attachment_ids=mail_id.attachment_ids.ids)
            mail_id.send()

    def build_report_name(self):
        equipment = self.maintenance_request_id.equipment_id.name if self.maintenance_request_id.equipment_id else ''
        request_num = self.maintenance_request_id.company_request_num
        report_name = _('Equipment[{equipment}] Intervention[{request_num}] Work and instruction report').format(equipment=equipment, request_num=request_num)
        return report_name

    def create_report_attachment(self):
        self.ensure_one()
        filename = self.build_report_name()
        pdf = self.build_report_as_pdf()
        attachment = self.env['ir.attachment'].create({
            'name': filename + '.pdf',
            'datas': base64.b64encode(pdf),
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })
        return attachment

    def action_preview_pdf(self):
        """ Manage View PDF action """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': ReportController.get_print_to_pdf_url(self),
            'target': 'new',
        }

    def build_report_as_pdf(self):
        """ Generate PDF report """
        self.ensure_one()
        if self.company_id == self.env.ref('cap_settings.company_tosa'):
            pdf = self.env.ref('cap_maintenance.action_print_detailed_work_done_report_tosa').with_context(lang=self.report_lang.code).render_qweb_pdf(res_ids=[self.id])[0]
        elif self.company_id == self.env.ref('cap_settings.company_traction'):
            pdf = self.env.ref('cap_maintenance.action_print_detailed_work_done_report_traction').with_context(lang=self.report_lang.code).render_qweb_pdf(res_ids=[self.id])[0]
        else:
            pdf = self.env.ref('cap_maintenance.action_print_detailed_work_done_report_puissance').with_context(lang=self.report_lang.code).render_qweb_pdf(res_ids=[self.id])[0]
            # for HTML report debugging purpose :  pdf = self.env.ref('cap_maintenance.action_print_detailed_work_done_report_puissance').with_context(lang=self.report_lang.code).render_qweb_html(self.ids, data=None)[0]
        return pdf
