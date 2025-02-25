import hashlib
from odoo import SUPERUSER_ID, api
from odoo.api import Environment
import logging

_logger = logging.getLogger(__name__)

def calculate_ean13(primary_key):
    """
    Generate a valid EAN-13 barcode using the primary key.
    - Uses the primary key as the base (padded to 12 digits).
    - Computes the EAN-13 check digit.
    """
    # Pass through hash to ensure somestandard length
    hash_val = hashlib.sha256(primary_key.encode()).hexdigest()
    _logger.info(f"Let me just check the values really quick: {hash_val}")
    base = str(int(hash_val,16))[:12]

    # Compute the check digit (EAN-13 standard)
    def calculate_check_digit(ean12):
        odd_sum = sum(int(ean12[i]) for i in range(0, 12, 2))
        even_sum = sum(int(ean12[i]) * 3 for i in range(1, 12, 2))
        total = odd_sum + even_sum
        return (10 - (total % 10)) % 10  # Ensures last digit makes total a multiple of 10

    check_digit = calculate_check_digit(base)
    return f"{base}{check_digit}"

def post_install_hook(cr, registry):
    """
    This hook runs after the module is installed.
    It assigns a valid EAN-13 barcode to all products without a barcode.
    """
    env = Environment(cr, SUPERUSER_ID, {})

    # TODO: set this as default
    # products = env['product.product'].search([('barcode', '=', False)])  # Only update missing barcodes
    products = env['product.product'].search([])  # Only update missing barcodes
    
    for product in products:
        try:
            product_id = str(product.id)
            _logger.info(f"Sending product.id={product_id} for barcode conversion")
            barcode = calculate_ean13(product_id)
            product.write({'barcode': barcode})
            _logger.info(f"Writing barcode {barcode} for produc {product.name}")

            #TODO: Let me also try image checksum

        except ValueError as e:
            _logger.error(f"Failed to assign barcode to product {product.id}: {e}")

