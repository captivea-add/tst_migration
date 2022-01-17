import base64
import os

from lxml import etree
import json

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

# fields that shouldnt be modified by non-manager users
_MANAGER_GROUP_RESTRICTED_FIELDS = [
    'name',
    'equipment_id',
    'bus_num',
    'request_date',
    'customer_partner_id',
    'customer_ref',
    'project_num',
    'request_type',
    'major_flaw',
    'consignment',
    'ccrp',
    'maintenance_type',
    'equipment_group',
    'equipment_subgroup',
    'flaw_origin',
    'manager_id',
    'mailing_list_preparation_partner_ids',
    'mailing_list_payment_partner_ids',
    'sap_assignment_num',
    'working_location_partner_id',
    'schedule_date',
    'end_date',
    'priority',
]


def yield_file_paths_from_directory_path(directory_path):
    """
    Yield file paths from given directory path.
    """
    for name in os.scandir(path=directory_path):
        element = os.path.join(directory_path, name)
        if os.path.isfile(element):
            yield element


# OVERRIDING MODEL
class MaintenanceRequest(models.Model):
    """
    Manage 'maintenance.request' model.
    Overriding model.
    """

    _name = 'maintenance.request'
    _inherit = ['maintenance.request', 'model.several.copy']

    #######################
    # ATTACHMENT RECOVERY #
    #######################

    attachment_recovery_directory_path = fields.Char(string="Attachment Recovery Directory Path")

    has_attachment_recovery_directory = fields.Boolean(string="Has Attachment Recovery Directory ?",
                                                       compute="compute_has_attachment_recovery_directory",
                                                       store=True)

    @api.depends("attachment_recovery_directory_path")
    def compute_has_attachment_recovery_directory(self):
        """
        Compute the 'has_attachment_recovery_directory' field value of some 'maintenance.request'.

        Maintenance request has one attachment recovery directory if and only if :
        - attachment recovery directory path is not empty
        - attachment recovery directory path directs to real system directory
        """
        for record in self:
            value = False
            if (record.attachment_recovery_directory_path
                    and os.path.isdir(record.attachment_recovery_directory_path)):
                value = True
            record.has_attachment_recovery_directory = value

    # ---------------------------------------------------------------------------------------------------------
    #                                       FIELDS DEFINTION
    # ---------------------------------------------------------------------------------------------------------

    # Numéro d'intervention
    company_request_num = fields.Char(string='Request Number', compute='compute_company_request_num', store=True)
    # Numéro de bus
    bus_num = fields.Char(string='Bus Num')
    # Client demandeur
    customer_partner_id = fields.Many2one(string='Customer', comodel_name='res.partner', check_company=True)
    # Référence client
    customer_ref = fields.Char(string='Customer Ref.')
    # N° Projet ABB / N° Projet Interne
    project_num = fields.Char(string='Internal Project N°')
    # Type d'intervention
    request_type = fields.Many2one(string='Maintenant Request Type', comodel_name='maintenance.request.type')

    # Défaut majeur
    major_flaw = fields.Many2one(comodel_name="maintenance.flaw", string="Major Flaw", check_company=True)
    # Cause du défaut
    flaw_origin = fields.Many2one(comodel_name="maintenance.flaw.origin", string="Flaw Origin", check_company=True)

    flaw_responsibility_id = fields.Many2one(comodel_name="maintenance.flaw.responsibility",
                                             string="Flaw Responsibility", check_company=True)

    # Consignation
    consignment = fields.Boolean(string='Consignment', default=True)
    # CCRP
    ccrp = fields.Char(string='CCRP')
    # Ensemble
    equipment_group = fields.Many2one(string='Group', comodel_name='maintenance.equipment.group', check_company=True)
    # Sous-ensemble
    equipment_subgroup = fields.Many2one(string='Subgroup', comodel_name='maintenance.equipment.subgroup', check_company=True, domain="[('equipment_group_id', '=', equipment_group)]")

    # Intervenant ABB / Intervenant sur site
    worker_ids = fields.Many2many(string='Workers', comodel_name='res.partner', relation='maintenance_request_worker_rel', domain="[('matricule', '!=', False), ('company_id', 'in', [company_id, False])]")
    # Responsable
    manager_id = fields.Many2one(string='Manager', comodel_name='res.users', required=True, default=lambda self: self.env.user, check_company=True)
    # Equipe : surchagée pour être masquée
    maintenance_team_id = fields.Many2one('maintenance.team', string='Maintenance Team', check_company=True, required=False)
    # Liste de diffusion préparation de l'intervention
    mailing_list_preparation_partner_ids = fields.Many2many(string='Mailing List Preparation',
                                                            comodel_name='res.partner',
                                                            relation='maintenance_request_mailing_list_preparation_partner_rel',
                                                            default=lambda self: self.env.company.mailing_list_preparation_partner_ids,
                                                            check_company=True)
    # Liste de diffusion des feuilles client
    mailing_list_work_report_partner_ids = fields.Many2many(string='Mailing List Customer Timesheet',
                                                            comodel_name='res.partner',
                                                            relation='maintenance_request_mailing_list_work_report_partner_rel',
                                                            default=lambda self: self.env.company.mailing_list_work_report_partner_ids,
                                                            check_company=True)
    # Liste de diffusion du rapport final
    mailing_list_final_report_partner_ids = fields.Many2many(string='Mailing List Final Report',
                                                             comodel_name='res.partner',
                                                             relation='maintenance_request_mailing_list_final_report_partner_rel',
                                                             check_company=True)
    # Liste de diffusion des frais
    mailing_list_payment_partner_ids = fields.Many2many(string='Mailing List Internal Timesheet',
                                                        comodel_name='res.partner',
                                                        relation='maintenance_request_mailing_list_hours_partner_rel',
                                                        default=lambda self: self.env.company.mailing_list_payment_partner_ids,
                                                        check_company=True)
    # Imputation
    sap_assignment_num = fields.Char(string='SAP Assignment Num')
    # Contacts sur le site
    on_site_partner_ids = fields.Many2many(string='On Site Partners', comodel_name='res.partner', domain="[('user_ids', '=', False), ('company_id', 'in', [company_id, False])]",
                                           relation='maintenance_request_on_site_partner_rel', column1='maintenance_request_id', column2='partner_id')
    # Adresse d'intervention
    working_location_partner_id = fields.Many2one(string='Working Location', comodel_name='res.partner', required=True, check_company=True)
    working_location = fields.Char(string='Working Location Address', related='working_location_partner_id.contact_address')
    # Date de début d'intervention (base field from Odoo)
    schedule_date = fields.Datetime(string='Start Date', required=True)
    # Date de fin d'intervention
    end_date = fields.Datetime(string='End Date', required=True)

    # -------------------------------------------------------------------
    # Descriptif et plan de travail
    # -------------------------------------------------------------------
    work_comment = fields.Html()

    # -------------------------------------------------------------------
    # Feuilles client
    # -------------------------------------------------------------------
    customer_timesheet_ids = fields.One2many(comodel_name='maintenance.timesheet', inverse_name='maintenance_request_id', domain="[('timesheet_type', '=', 'customer')]")
    customer_timesheet_count = fields.Integer(string='Customer Timesheet Count', compute='compute_customer_timesheet_count')

    # -------------------------------------------------------------------
    # Feuilles d'heures interne
    # -------------------------------------------------------------------
    internal_timesheet_ids = fields.One2many(comodel_name='maintenance.timesheet', inverse_name='internal_maintenance_request_id', domain="[('timesheet_type', '=', 'internal')]")
    internal_timesheet_count = fields.Integer(string='Internal Timesheet Count', compute='compute_internal_timesheet_count')

    # -------------------------------------------------------------------
    # Organisation du voyage
    # -------------------------------------------------------------------
    maintenance_travel_ids = fields.One2many(comodel_name='maintenance.travel', inverse_name='maintenance_request_id')

    travels_count = fields.Integer(string='Travels Count', compute='compute_travels_count')

    # -------------------------------------------------------------------
    # Consignation électrique
    # -------------------------------------------------------------------
    consignment_ids = fields.One2many(comodel_name='maintenance.consignment', inverse_name='maintenance_request_id')

    # -------------------------------------------------------------------
    # Déconsignation électrique
    # -------------------------------------------------------------------
    deconsignment_ids = fields.One2many(comodel_name='maintenance.consignment', inverse_name='deconsignment_maintenance_request_id')

    # -------------------------------------------------------------------
    # Document sécurité complémentaire
    # -------------------------------------------------------------------
    security_document_ids = fields.Many2many(comodel_name='ir.attachment')

    # -------------------------------------------------------------------
    # Take 5
    # -------------------------------------------------------------------
    takefive_ids = fields.One2many(comodel_name='maintenance.consignment', inverse_name='takefive_maintenance_request_id')

    # -------------------------------------------------------------------
    # Outillage
    # -------------------------------------------------------------------
    tools_maintenance_tool_ids = fields.One2many(comodel_name='maintenance.tool', inverse_name='tools_maintenance_request_id')

    tools_count = fields.Integer(string='Tools Count', compute='compute_tools_count')

    # -------------------------------------------------------------------
    # Pièces de rechange
    # -------------------------------------------------------------------
    spare_parts_maintenance_tool_ids = fields.One2many(comodel_name='maintenance.tool', inverse_name='spare_parts_maintenance_request_id')

    spare_parts_count = fields.Integer(string='Spare Parts Count', compute='compute_spare_parts_count')

    # -------------------------------------------------------------------
    # Rapports d'intervention détaillés
    # -------------------------------------------------------------------
    detailed_report_work_done_ids = fields.One2many(comodel_name='maintenance.detailed.report.work.done', inverse_name='maintenance_request_id')

    detailed_report_work_done_count = fields.Integer(string='Detailed Report Work Done Count', compute='compute_detailed_report_work_done_count')

    # ---------------------------------------------------------------------------------------------------------
    #                                       FIELDS CALCULATION
    # ---------------------------------------------------------------------------------------------------------

    def compute_detailed_report_work_done_count(self):
        for record in self:
            record.detailed_report_work_done_count = len(record.detailed_report_work_done_ids)

    def compute_internal_timesheet_count(self):
        for record in self:
            record.internal_timesheet_count = len(record.internal_timesheet_ids)

    def compute_customer_timesheet_count(self):
        for record in self:
            record.customer_timesheet_count = len(record.customer_timesheet_ids)

    def compute_travels_count(self):
        for record in self:
            record.travels_count = len(record.maintenance_travel_ids)

    def compute_tools_count(self):
        for record in self:
            record.tools_count = len(record.tools_maintenance_tool_ids)

    def compute_spare_parts_count(self):
        for record in self:
            record.spare_parts_count = len(record.spare_parts_maintenance_tool_ids)

    @api.onchange('on_site_partner_ids')
    def onchange_on_site_partner_ids(self):
        domain = []
        if self.on_site_partner_ids and self.on_site_partner_ids.child_ids:
            possible_location_ids = self.on_site_partner_ids.child_ids.filtered(lambda c: c.type != 'contact')._origin
            domain += [('id', 'in', possible_location_ids.ids)]
        if self.on_site_partner_ids:
            new_partner_ids = self.on_site_partner_ids - self._origin.on_site_partner_ids
            self.mailing_list_work_report_partner_ids += new_partner_ids - self.mailing_list_work_report_partner_ids

        return {'domain': {'working_location_partner_id': domain}}

    @api.depends('company_id.maintenance_request_sequence_id')
    def compute_company_request_num(self):
        """ Number depends on company. Each company has it's own sequence. """
        for record in self:
            if record.company_id.maintenance_request_sequence_id:
                record.company_request_num = record.company_id.maintenance_request_sequence_id.next_by_id()

    @api.onchange('worker_ids')
    def onchange_worker_ids(self):
        """ Every worker should be included in preparation mailing list """
        for record in self:
            if record.worker_ids not in record.mailing_list_preparation_partner_ids:
                record.mailing_list_preparation_partner_ids += record.worker_ids

    @api.onchange('manager_id')
    def onchange_manager_id(self):
        """ Make sure manager_id is always in work report mailing list """
        for record in self:
            if record.manager_id.partner_id not in record.mailing_list_preparation_partner_ids:
                record.mailing_list_preparation_partner_ids += record.manager_id.partner_id

            if record.manager_id.partner_id not in record.mailing_list_work_report_partner_ids:
                record.mailing_list_work_report_partner_ids += record.manager_id.partner_id

            if record.manager_id.partner_id not in record.mailing_list_payment_partner_ids:
                record.mailing_list_payment_partner_ids += record.manager_id.partner_id

    @api.constrains('schedule_date', 'end_date')
    def _check_working_dates(self):
        for record in self:
            if record.schedule_date and record.end_date and record.schedule_date > record.end_date:
                raise ValidationError(_('End date must be greater than Start Date.'))

    def open_all_ui(self):
        """
            Redirect to specific template in order to open several tabs
            Useful to manage offline operations
         """
        action = {
            'type': 'ir.actions.act_url',
            'url': '/cap_maintenance/offline/maintenance_request/{}'.format(self.id),
            'target': 'new',
        }
        return action

    def action_maintenance_travel_tree(self):
        """ Go to Travel arrangement tree view
            with ability to insert new records linked to current maitenance.request
        """
        action_rec = self.env.ref('cap_maintenance.action_maintenance_travel')
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update({'default_maintenance_request_id': self.id})
        action['context'] = ctx
        action['domain'] = [('maintenance_request_id', '=', self.id)]

        return action

    def action_maintenance_tools_tree(self):
        """ Go to Tools tree view
            with ability to insert new records linked to current maitenance.request
        """
        action_rec = self.env.ref('cap_maintenance.action_maintenance_tool')
        action = action_rec.read()[0]
        action['display_name'] = _("Tools")
        action['views'] = [
            (self.env.ref('cap_maintenance.maintenance_tool_view_tree_01').id, 'tree'),
            (self.env.ref('cap_maintenance.maintenance_tool_view_form_01').id, 'form'),
        ]
        ctx = dict(self.env.context)
        ctx.update({'default_tools_maintenance_request_id': self.id})
        action['context'] = ctx
        action['domain'] = [('tools_maintenance_request_id', '=', self.id)]
        return action

    def action_maintenance_spare_parts_tree(self):
        """ Go to Spare Parts tree view
            with ability to insert new records linked to current maitenance.request
        """
        action_rec = self.env.ref('cap_maintenance.action_maintenance_tool')
        action = action_rec.read()[0]
        action['display_name'] = _("Spare Parts")
        action['views'] = [
            (self.env.ref('cap_maintenance.maintenance_tool_view_tree_02').id, 'tree'),
            (self.env.ref('cap_maintenance.maintenance_tool_view_form_02').id, 'form'),
        ]
        ctx = dict(self.env.context)
        ctx.update({'default_spare_parts_maintenance_request_id': self.id, 'default_assignment': self.sap_assignment_num})
        action['context'] = ctx
        action['domain'] = [('spare_parts_maintenance_request_id', '=', self.id)]
        return action

    def action_customer_timesheet_tree(self):
        """ Go to Customer Timesheet tree view
            with ability to insert new records linked to current maitenance.request
        """
        action_rec = self.env.ref('cap_maintenance.action_maintenance_timesheet')
        action = action_rec.read()[0]
        action['display_name'] = _("Customer Timesheets")
        action['views'] = [
            (self.env.ref('cap_maintenance.maintenance_timesheet_view_tree_01').id, 'tree'),
            (self.env.ref('cap_maintenance.maintenance_timesheet_view_form_01').id, 'form'),
        ]
        ctx = dict(self.env.context)
        ctx.update({
            'default_timesheet_type': 'customer',
            'default_manager_id': self.manager_id.id,
            'default_maintenance_request_id': self.id,
        })
        action['context'] = ctx
        action['domain'] = [('maintenance_request_id', '=', self.id)]
        return action

    def action_internal_timesheet_tree(self):
        """ Go to Internal Timesheet tree view
            with ability to insert new records linked to current maitenance.request
        """
        if any(self.filtered(lambda r: not r.takefive_ids)):
            raise UserError(_("Please fill Take 5 form first."))
        else:
            action_rec = self.env.ref('cap_maintenance.action_maintenance_timesheet')
            action = action_rec.read()[0]
            action['display_name'] = _("Internal Timesheets")
            action['views'] = [
                (self.env.ref('cap_maintenance.maintenance_timesheet_view_tree_02').id, 'tree'),
                (self.env.ref('cap_maintenance.maintenance_timesheet_view_form_02').id, 'form'),
            ]
            ctx = dict(self.env.context)
            ctx.update({
                'default_timesheet_type': 'internal',
                'default_manager_id': self.manager_id.id,
                'default_internal_maintenance_request_id': self.id,
            })
            action['context'] = ctx
            action['domain'] = [('internal_maintenance_request_id', '=', self.id)]
            return action

    def action_detailed_report_work_done_tree(self):
        """ Go to Detailed Report Work Done tree view
            with ability to insert new records linked to current maitenance.request
        """
        action_rec = self.env.ref('cap_maintenance.action_detailed_report_work_done')
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update({'default_maintenance_request_id': self.id, 'default_company_id': self.company_id.id, 'default_manager_id': self.manager_id.id, 'default_start_date': self.schedule_date, 'default_end_date': self.end_date})
        action['context'] = ctx
        action['domain'] = [('maintenance_request_id', '=', self.id)]

        return action

    def build_report_name(self):
        equipment = self.equipment_id.name if self.equipment_id else ''
        report_name = _('Equipment[{equipment}] Intervention[{request_num}] Preparation').format(equipment=equipment, request_num=self.company_request_num)
        return report_name

    def send_mail_preparation(self):
        """
            Sends an email to mailing_list_preparation_partner_ids
        """
        for record in self:
            template = self.env.ref('cap_maintenance.worker_preparation_mail_template')
            message_id = template.with_context(lang=self.env.user.lang, model=self._name, res_id=self, active_ids=[self]).sudo().send_mail(self.id)
            mail_id = self.env['mail.mail'].browse([message_id])
            record.message_post(subject=mail_id.subject, body=mail_id.body_html, attachment_ids=mail_id.attachment_ids.ids)
            mail_id.send()
            record.is_email_sent = True

    def raise_if_missing_form(self):
        """ Returns True if consignement field is True AND consignement / deconsignement / take5 are filled
            OR
            consignement field is False AND take5 is filled

            consignement / deconsignement / take5 are considered as filled if : attachment_ids is set
        """
        for record in self:
            missing_takefive_records = (record.takefive_ids and record.takefive_ids.filtered(lambda r: not r.has_attachment)) or not record.takefive_ids
            missing_consignment_records = (record.consignment_ids and record.consignment_ids.filtered(lambda r: not r.has_attachment)) or not record.consignment_ids
            missing_deconsignment_records = (record.deconsignment_ids and record.deconsignment_ids.filtered(lambda r: not r.has_attachment)) or not record.deconsignment_ids

            if missing_takefive_records:
                raise UserError(_("Operation not allowed.\nTake 5 is missing."))
            if record.consignment and missing_consignment_records:
                raise UserError(_("Operation not allowed.\nElectrical Consignment is missing."))
            if record.consignment and missing_deconsignment_records:
                raise UserError(_("Operation not allowed.\nElectrical DeConsignment is missing."))
            else:
                return True

    @api.constrains('stage_id', 'worker_ids')
    def _check_mandatory_workers(self):
        for record in self:
            if record.stage_id != self.env.ref('cap_maintenance.stage_not_assigned') and not record.worker_ids:
                raise ValidationError(_('Workers are missing.'))

    @api.model
    def create_attachment_from_file_path(self, file_path):
        """
        Create one 'ir.attachment' from given file path and attach it to one 'maintenance.request'.
        """
        with open(file_path, "rb") as file:
            data = base64.b64encode(file.read())
        args = {"name": os.path.basename(file_path),
                "description": file_path,
                "datas": data,
                "res_model": self._name,
                "res_id": self.id}
        return self.env["ir.attachment"].create(args)

    @api.model
    def has_attachment_with_name(self, name):
        """
        Return True if 'maintenance.request' has at least one 'ir.attachment' with given name.
        Return False otherwise.
        """
        domain = [("res_model", "=", self._name),
                  ("res_id", "=", self.id),
                  ("name", "=", name)]
        return bool(self.env["ir.attachment"].search(domain, limit=1))
            
    def recover_attachments(self):
        """
        Create some 'ir.attachment' from some 'maintenance.request'.

        For every file from attachment recovery directory path, create one attachment to maintenance request.
        If maintenance request has no attachment recovery directory, ignore it and continue to next one.
        If maintenance request has attachment with file name as name already, ignore it and continue to next one.
        """
        for record in self.filtered("has_attachment_recovery_directory"):
            directory_path = record.attachment_recovery_directory_path
            for file_path in yield_file_paths_from_directory_path(directory_path=directory_path):
                if not record.has_attachment_with_name(name=os.path.basename(file_path)):
                    record.create_attachment_from_file_path(file_path=file_path)

    @api.model
    def recover_attachments_for_all_records(self):
        """
        Recover 'ir.attachment' for all existing 'maintenance.request'.

        This method is designed to be called through an 0-number-call 'ir.cron'.
        This cron could be considered as a global attachment recovery helper.
        """
        self.env["maintenance.request"].search([]).recover_attachments()

    ####################
    # CORE ORM METHODS # 
    ####################

    # OVERRIDING METHOD
    @api.model
    def create(self, args):
        """
        Create one 'maintenance.request' with given args.
        Overriding method.

        I this override :
        - we run attachment recovery mechanism.
        """
        # CALL SUPER
        record = super(MaintenanceRequest, self).create(args)
        # RECOVER ATTACHMENTS
        record.recover_attachments()
        # CONFIRM CREATION
        return record

    # OVERRIDING METHOD
    def write(self, args):
        """
        Edit some 'maintenance.request' with given args.
        Overriding method.

        In this override :
        - we send preparation email if stage changes from 'Not Assigned' to 'In Progress',
        - we run attachment recovery mechanism.
        """
        # SEND EMAIL PREPARATION - PART 1/2
        records_for_send_preparation_mail = self.env[self._name]
        if args.get('stage_id', False) == self.env.ref('cap_maintenance.stage_in_progress').id:
            records_for_send_preparation_mail = self.filtered(
                lambda r: r.stage_id == self.env.ref('cap_maintenance.stage_not_assigned'))
        # CALL SUPER
        res = super(MaintenanceRequest, self).write(args)
        if res is not True:
            return res
        # SEND EMAIL PREPARATION - PART 2/2
        records_for_send_preparation_mail.send_mail_preparation()
        # RECOVER ATTACHMENTS
        self.recover_attachments()
        # CONFIRM MODIFICATIONS
        return True

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        res = super(MaintenanceRequest, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            has_manager_group = self.env.ref('maintenance.group_equipment_manager') in self.env.user.groups_id
            if not has_manager_group:
                view_content = etree.XML(res['arch'])
                for node in view_content.xpath("//field"):
                    if node.attrib['name'] in _MANAGER_GROUP_RESTRICTED_FIELDS:
                        node.set('readonly', '1')
                        node.set('modifiers', json.dumps({"readonly": True}))
                        res['arch'] = etree.tostring(view_content)

        return res
