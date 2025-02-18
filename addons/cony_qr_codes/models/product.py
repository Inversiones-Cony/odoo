import base64
import hashlib
import qrcode
import io

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qr_code = fields.Binary("QR Code", compute="_compute_qr_code", store=True)
    image_checksum = fields.Char("Image Checksum", compute="_compute_image_checksum", store=True)

    @api.depends('id')  # Only computed once based on the product ID
    def _compute_qr_code(self):
        for product in self:
            if not product.qr_code:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(f"product:{product.id}")  # Use an immutable identifier
                qr.make(fit=True)

                img = qr.make_image(fill="black", back_color="white")
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                product.qr_code = base64.b64encode(img_bytes.getvalue())

    @api.depends('image_1920')  # Recalculate only when the image changes
    def _compute_image_checksum(self):
        for product in self:
            if product.image_1920:
                checksum = hashlib.sha256(base64.b64decode(product.image_1920)).hexdigest()
                product.image_checksum = checksum
            else:
                product.image_checksum = False

