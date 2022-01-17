import base64

from odoo import models, fields, api

from odoo.exceptions import UserError
from odoo.tools.translate import GettextAlias

_ = GettextAlias()


class MaintenanceConsignment(models.Model):
    _name = "maintenance.consignment"
    _description = "Consignment"

    maintenance_request_id = fields.Many2one(comodel_name="maintenance.request")
    deconsignment_maintenance_request_id = fields.Many2one(comodel_name="maintenance.request")
    takefive_maintenance_request_id = fields.Many2one(comodel_name="maintenance.request")

    type_values = [("none", "None"), ("abb", "Hitachi"), ("customer", "Others (Files, photos)")]
    type = fields.Selection(selection=type_values, default="none", required=True)

    attachment_ids = fields.Many2many(string="File", comodel_name="ir.attachment")

    picture_name = fields.Char(string="Picture Name", store=False)
    picture = fields.Binary(string="Picture", attachment=False, store=False)

    has_attachment = fields.Boolean(string="Has Attachment", compute="compute_has_attachment")

    survey_id = fields.Many2one(comodel_name="survey.survey", compute="_compute_survey_id", readonly=True, store=True)
    response_id = fields.Many2one("survey.user_input", "Response", ondelete="set null", readonly=True)
    response_state = fields.Selection(related="response_id.state", store=True)
    response_line_ids = fields.One2many(comodel_name="survey.user_input_line", inverse_name="consignment_input_id",
                                        related="response_id.user_input_line_ids")

    # DEFINE GOOD SURVEY DEPENDS TYPE
    @api.depends("maintenance_request_id", "takefive_maintenance_request_id", "deconsignment_maintenance_request_id")
    def _compute_survey_id(self):
        for record in self:
            if record.maintenance_request_id:
                record.survey_id = self.env.ref("cap_maintenance.survey_electrical_consignment")
            elif record.deconsignment_maintenance_request_id:
                record.survey_id = self.env.ref("cap_maintenance.survey_electrical_deconsignment")
            elif record.takefive_maintenance_request_id:
                record.survey_id = self.env.ref("cap_maintenance.survey_take_5")

        return True

    @api.onchange("type")
    def _onchange_type(self):
        self._compute_survey_id()

    @api.onchange("picture")
    def _onchange_picture(self):
        datas = self.picture
        if datas:
            attachment_id = self.env["ir.attachment"].create({
                            "name": self.picture_name,
                            "res_model": self._name,
                            "res_field": "attachment_ids",
                            "res_id": self.id,
                            "type": "binary",
                            "datas": datas,
                        })
            self.attachment_ids = attachment_id

    def compute_has_attachment(self):
        for record in self:
            record.has_attachment = bool(record.attachment_ids)

    @api.onchange("attachment_ids")
    def onchange_attachment_ids(self):
        """ Force max 1 consignment file at a time """
        if self.attachment_ids and len(self.attachment_ids) > 1:
            self.attachment_ids = self.attachment_ids[1]
        elif not self.attachment_ids:
            self.picture_name = None
            self.picture = None

    def action_start_survey(self):
        self.ensure_one()
        # create a response and link it to this consignment
        if not self.response_id:
            response = self.survey_id._create_answer()
            self.response_id = response.id
            # To bypass survey start page and create link between consignment and survey user input
            self.response_id.update({"state": "skip", "consignment_id": self.id})
        else:
            response = self.response_id

        # grab the token of the response and start surveying
        action = self.survey_id.with_context(survey_token=response.token).action_start_survey()
        action["target"] = "new"
        return action

    def generate_pdf(self):
        self.attachment_ids = self._print_survey()

    def _print_survey(self):
        if not self.has_attachment and self.response_id:
            data = self.env["survey.question.answer"].get_result_report_data(self.response_id)

            pdf_name = _("survey")
            maintenance_request = self.env["maintenance.request"]
            if self.maintenance_request_id:
                pdf_name = _("consignment")
                maintenance_request = self.maintenance_request_id
            elif self.deconsignment_maintenance_request_id:
                pdf_name = _("deconsignment")
                maintenance_request = self.deconsignment_maintenance_request_id
            elif self.takefive_maintenance_request_id:
                pdf_name = _("take_5")
                maintenance_request = self.takefive_maintenance_request_id
            data["maintenance_request"] = maintenance_request

            pdf_bin, content_type = self.env.ref("cap_survey_report.action_print_survey_report")\
                .sudo().render_qweb_pdf(data=data)

            args = {"name": pdf_name,
                    "description": pdf_name,
                    "datas": base64.b64encode(pdf_bin),
                    "res_model": self._name,
                    "res_id": self.id}
            attachment_id = self.env["ir.attachment"].create(args)

            return attachment_id
        else:
            return False

    def _validate_survey_completed(self):
        for record in self:
            if record.type == "abb" and record.survey_id:
                if record.response_id and not record.response_line_ids:
                    raise UserError(_("You must complete {} form before saving.".format(record.survey_id.display_name)))

    @api.model
    def create(self, args):
        # Make sure survey is completed
        self._validate_survey_completed()
        res = super(MaintenanceConsignment, self).create(args)
        return res

    @api.model
    def write(self, args):
        for record in self:
            # When survey is in progress
            if record.type == "abb" or args.get("type") == "abb":
                if "response_id" in args:
                    pass
                else:
                    # Make sure survey is completed
                    if record.response_state != "done":
                        message = _("You must complete {} form before saving.")
                        message = message.format(record.survey_id.display_name)
                        raise UserError(message)

                    if record.response_state == "done":
                        if not record.has_attachment and "attachment_ids" not in args:
                            args["attachment_ids"] = [(6, 0, [record._print_survey().id])]

            res = super(MaintenanceConsignment, self).write(args)
            if res is not True:
                return res

        return True

    def prepare_offline_management(self, **kwargs):
        """
            Create a new consignment record and begin associated survey

            ::return: survey url
        """
        if not kwargs:
            raise ValueError("Do not forget to provide maintenance.request id !")

        values = {"type": "abb"}
        values.update(kwargs)
        new_consignment = self.create(values)

        action = new_consignment.action_start_survey()
        return action["url"]
