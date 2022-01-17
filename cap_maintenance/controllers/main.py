from odoo import http, _
from odoo.http import request


class ReportController(http.Controller):

    @staticmethod
    def get_print_to_pdf_url(record):
        return '/cap_maintenance/print_to_pdf/{model}/{id}'.format(model=record._name, id=record.id)

    @http.route('/cap_maintenance/print_to_pdf/<string:res_model>/<int:res_id>', methods=['POST', 'GET'], csrf=False, type='http', auth="user")
    def print_to_pdf(self, res_model, res_id, **kw):
        record = request.env[res_model].browse([res_id])
        pdf = record.build_report_as_pdf()
        pdfhttpheaders = [
            ('Content-Disposition', 'inline; filename=' + record.build_report_name() + ".pdf;"),
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)
        # for HTML report debugging purpose : return request.make_response(pdf)

    @http.route('/cap_maintenance/offline/maintenance_request/<int:maintenance_request_id>', methods=['POST', 'GET'], csrf=False, type='http', auth="user")
    def open_all_ui(self, maintenance_request_id):

        maintenance_request_id = request.env['maintenance.request'].browse([maintenance_request_id])

        urls_to_open = []
        consignment_model = request.env['maintenance.consignment']
        # Ouvrir les sondages :
        # - Consignation
        urls_to_open.append(consignment_model.prepare_offline_management(maintenance_request_id=maintenance_request_id.id))
        # - Déconsignation
        urls_to_open.append(consignment_model.prepare_offline_management(deconsignment_maintenance_request_id=maintenance_request_id.id))
        # - Take 5
        urls_to_open.append(consignment_model.prepare_offline_management(takefive_maintenance_request_id=maintenance_request_id.id))

        return request.render('cap_maintenance.offline_starting_view', qcontext={'urls_to_open': urls_to_open})
