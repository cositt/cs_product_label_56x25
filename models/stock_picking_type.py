from odoo import fields, models

from .constants import LABEL_FORMAT, LABEL_FORMAT_NAME


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    # Allows "Auto print product labels" on receipts with this format.
    product_label_format = fields.Selection(
        selection_add=[(LABEL_FORMAT, LABEL_FORMAT_NAME)],
        ondelete={LABEL_FORMAT: 'set default'},
    )
