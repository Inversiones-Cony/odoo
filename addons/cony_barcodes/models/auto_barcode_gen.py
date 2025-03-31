from odoo import api, models

class BarcodeLabelPrinter(models.Model):
    _inherit = 'product.template'

    def action_generate_ean13(self):
        """Generate a unique EAN13 barcode based on product ID."""
        for product in self:
            # if not product.barcode:
            if True:
                product.barcode = self._generate_ean13_from_id(product.id)
                
    def _generate_ean13_from_id(self, product_id):
        """Generate EAN13 from product ID."""
        # Convert product ID to string and pad with zeros to make 12 digits
        company_prefix = self.env['ir.config_parameter'].sudo().get_param('company.barcode.prefix', '000')
        # Use company prefix + product ID, padded to 12 digits total
        ean = company_prefix + str(product_id).zfill(12 - len(company_prefix))
        
        # Ensure we have exactly 12 digits before adding check digit
        ean = ean[:12]
        
        # Calculate check digit
        total = 0
        for i, digit in enumerate(ean):
            weight = 1 if i % 2 == 0 else 3
            total += int(digit) * weight
        check_digit = (10 - (total % 10)) % 10
        
        # Complete EAN13 code
        return ean + str(check_digit)
    
    @api.model
    def action_generate_ean13_multi(self):
        """Generate EAN13 barcodes for selected products."""
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])
        
        count = 0
        if active_model == 'product.template':
            templates = self.browse(active_ids)
            for template in templates:
                # if not template.barcode:
                template.action_generate_ean13()
                count += 1
        elif active_model == 'product.product':
            products = self.env['product.product'].browse(active_ids)
            for product in products:
                # if not product.barcode:
                product.barcode = self._generate_ean13_from_id(product.id)
                count += 1
        
        # Return a client notification action
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Barcodes Generated',
                'message': f'{count} product(s) had barcodes generated.',
                'sticky': False,
                'type': 'success',
            }
        }
