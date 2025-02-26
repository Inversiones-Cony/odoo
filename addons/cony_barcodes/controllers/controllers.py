# -*- coding: utf-8 -*-
# from odoo import http


# class ConyBarcodes(http.Controller):
#     @http.route('/cony_barcodes/cony_barcodes', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cony_barcodes/cony_barcodes/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cony_barcodes.listing', {
#             'root': '/cony_barcodes/cony_barcodes',
#             'objects': http.request.env['cony_barcodes.cony_barcodes'].search([]),
#         })

#     @http.route('/cony_barcodes/cony_barcodes/objects/<model("cony_barcodes.cony_barcodes"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cony_barcodes.object', {
#             'object': obj
#         })
