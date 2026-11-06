{
    'name': 'Etiqueta de producto 56 x 25 mm (PDF, impresión directa)',
    'version': '19.0.1.0.0',
    'summary': 'Etiqueta PDF de 56 x 25 mm para impresoras de etiquetas con driver de Windows, '
               'imprimible desde productos y recepciones sin IoT',
    'author': 'Cositt Technology®',
    'website': 'https://cositt.com',
    'category': 'Inventory/Inventory',
    'license': 'LGPL-3',
    'depends': ['stock'],
    'data': [
        'report/report_label_56x25.xml',
        'report/label_56x25_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cs_product_label_56x25/static/src/js/label_direct_print.js',
        ],
    },
    'installable': True,
    'application': False,
}
