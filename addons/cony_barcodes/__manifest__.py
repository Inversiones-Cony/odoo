# -*- coding: utf-8 -*-
{
    'name': "Product Barcode Printing.",

    'summary': """
        Will take care of generating and reporting sensible barcodes.
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Huginns",
    'website': "https://www.huginns.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'web'],

    # always loaded
    'data': [
        'reports/product_label_report.xml',
        'views/product_barcode_gen.xml',
    ],
    # only loaded in demonstration mode
}
