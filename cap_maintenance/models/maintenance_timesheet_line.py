from odoo import models, fields, api


class MaintenanceTimesheetLine(models.Model):
    _name = 'maintenance.timesheet.line'
    _description = 'Maintenance Timesheet Line'

    maintenance_timesheet_id = fields.Many2one(comodel_name='maintenance.timesheet')

    # Champ technique : 1 - 31
    sequence = fields.Integer(string='Day', readonly=True)

    # Heures normales
    regular_hours = fields.Integer(string='Regular Hours')
    # Temps de voyage
    travelling_hours = fields.Integer(string='Travelling Hours')
    # Heures d'attentes et de préparation
    waiting_hours = fields.Integer(string='Waiting/Preparation Hours')
    # Heures supplémentaires (23h - 6h)
    extra_hours = fields.Integer(string='Extra Hours 6AM-11PM')
    # Heures de nuit (6h - 23h)
    night_hours = fields.Integer(string='Night Hours 11PM-6AM')
    # Heures supplémentaires de nuit ou heures de travai dimanche et jours feriés
    extra_night_and_holiday_hours = fields.Integer(string='Extra Night Hours and Holiday')
    # Total des heures
    total_hours = fields.Integer(string='Total Hours', compute='compute_total_hours')
    # Km
    kilometers = fields.Integer(string='km')

    # -------------------------------------------------------------------------------------------
    #                                   CALCULATED FIELDS
    # -------------------------------------------------------------------------------------------

    @api.depends('regular_hours', 'travelling_hours', 'waiting_hours', 'extra_hours', 'night_hours', 'extra_night_and_holiday_hours')
    def compute_total_hours(self):
        for record in self:
            record.total_hours = record.regular_hours + record.travelling_hours + record.waiting_hours + record.extra_hours + record.night_hours + record.extra_night_and_holiday_hours

