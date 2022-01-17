from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class MaintenanceTravel(models.Model):
    _name = 'maintenance.travel'
    _description = 'Maintenance Travel'

    name = fields.Char(compute='compute_name', translate=True)

    maintenance_request_id = fields.Many2one(comodel_name='maintenance.request')

    # Hôtel
    is_hotel = fields.Boolean(string='Hotel')
    # Date d'arrivée
    hotel_date_from = fields.Date(string='From')
    # Date de départ
    hotel_date_to = fields.Date(string='To')
    # Adresse de l'hôtel
    hotel_additional_info = fields.Char(string='Hotel Additional Information')

    # Voiture
    is_company_car = fields.Boolean(string='Company Car')
    is_chsec = fields.Boolean(string='CHSEC')
    is_car_rental = fields.Boolean(string='Car Rental')
    car_date_from = fields.Date(string='From')
    car_date_to = fields.Date(string='To')
    car_additional_info = fields.Char(string='Car Additional Information')

    # Vol
    is_flight = fields.Boolean(string='Flight')
    flight_date_to_destination = fields.Date(string='Outbound Flight')
    flight_date_return = fields.Date(string='Return Flight')
    flight_additional_info = fields.Char(string='Flight Additional Information')

    trip_additionnal_info = fields.Char(string='Trip Additional Information')

    # Pièces jointes
    attachment_ids = fields.Many2many(string='File', comodel_name='ir.attachment')
    has_attachment = fields.Boolean(string='Has Attachment', compute='compute_has_attachment')

    @api.onchange('hotel_date_from', 'hotel_date_to')
    @api.constrains('hotel_date_from', 'hotel_date_to')
    def _check_hotel_dates(self):
        for record in self:
            if record.hotel_date_from and record.hotel_date_to and record.hotel_date_from > record.hotel_date_to:
                raise ValidationError(_('Travel arrangements : Hotel leaving date must be greater than arrival date.'))

    @api.onchange('car_date_from', 'car_date_to')
    @api.constrains('car_date_from', 'car_date_to')
    def _check_car_dates(self):
        for record in self:
            if record.car_date_from and record.car_date_to and record.car_date_from > record.car_date_to:
                raise ValidationError(_('Travel arrangements : Car return date must be greater than start date.'))

    @api.onchange('flight_date_to_destination', 'flight_date_return')
    @api.constrains('flight_date_to_destination', 'flight_date_return')
    def _check_flight_dates(self):
        for record in self:
            if record.flight_date_to_destination and record.flight_date_return and record.flight_date_to_destination > record.flight_date_return:
                raise ValidationError(_('Travel arrangements : Flight return date must be greater than departure date.'))

    def compute_name(self):
        for record in self:
            all_travels = record.search([('maintenance_request_id', '=', record.maintenance_request_id.id)])
            sequence = list(all_travels).index(record) + 1
            record.name = _("Travel N°{}").format(sequence)

    def compute_has_attachment(self):
        for record in self:
            record.has_attachment = bool(record.attachment_ids)

    def find_all_tools(self):
        self.ensure_one()
        return self.env['maintenance.tool'].find_all_tools_by_request_and_travel(self.maintenance_request_id, self)

    def find_all_spare_parts(self):
        self.ensure_one()
        return self.env['maintenance.tool'].find_all_spare_part_by_request_and_travel(self.maintenance_request_id, self)
