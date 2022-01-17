from odoo import models, fields, api


class AttachmentPicture(models.Model):
    _name = 'attachment.picture'
    _description = 'Picture Attachment'

    customer_timesheet_before_work_attachment_ids = fields.Many2one(comodel_name='maintenance.timesheet')
    customer_timesheet_after_work_attachment_ids = fields.Many2one(comodel_name='maintenance.timesheet')
    detailed_report_work_done_ids = fields.Many2one(comodel_name='maintenance.detailed.report.work.done')

    picture = fields.Binary(string='Picture', attachment=True, required=True)
    datetime = fields.Datetime(string='Date', default=fields.Datetime.now)

    picture_name = fields.Char(string='Name')
