from odoo import models, fields
import base64
import barcode
from barcode.writer import ImageWriter
from io import BytesIO

class ProductBarcodeLabel(models.TransientModel):
    _name = 'product.barcode.label'
    _description = 'Generate Barcode Labels for Selected Products'

    product_ids = fields.Many2many('product.template', string="Products")

    def generate_barcodes(self):
        report_action = self.env.ref('your_module.report_product_barcode')
        return report_action.report_action(self.product_ids)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def generate_barcode_base64(self):
        """Generates a barcode image dynamically as a base64-encoded PNG."""
        for record in self:
            if not record.barcode:
                return False
            buffer = BytesIO()
            barcode_class = barcode.get_barcode_class('EAN13')
            barcode_instance = barcode_class(record.barcode, writer=ImageWriter())
            barcode_instance.write(buffer)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')


