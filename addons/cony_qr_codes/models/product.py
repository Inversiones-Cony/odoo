import base64
import hashlib
import qrcode
import io
import hashlib

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    image_checksum = fields.Char(
        "Image Checksum", compute="_compute_image_checksum", store=True
    )

    @api.model
    def init(self):
        self._cr.execute("SELECT id FROM product_template WHERE image_checksum IS NULL")
        product_ids = [row[0] for row in self._cr.fetchall()]

        if product_ids:
            products = self.env["product.template"].browse(product_ids)
            products._compute_image_checksum()

    @api.depends("image_1920")  # Recalculate only when the image changes
    def _compute_image_checksum(self):
        for product in self:
            if product.image_1920:
                checksum = hashlib.sha256(
                    base64.b64decode(product.image_1920)
                ).hexdigest()
                product.image_checksum = checksum
            else:
                product.image_checksum = False
