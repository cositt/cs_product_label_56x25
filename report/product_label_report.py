import html

from odoo import api, models
from odoo.addons.product.report.product_label_report import _prepare_data

from ..models.constants import SHOP_NAME_DEFAULT, SHOP_NAME_PARAM


class ReportProductLabel56x25(models.AbstractModel):
    _name = 'report.cs_product_label_56x25.report_label_56x25'
    _description = 'Product Label 56 x 25 mm'

    @api.model
    def _get_report_values(self, docids, data):
        values = _prepare_data(self.env, docids, self._normalize_data(data or {}))
        return {
            **values,
            'label_name': self._label_name,
            'label_variant': self._label_variant,
            'shop_name': self._shop_name(),
        }

    @api.model
    def _shop_name(self) -> str:
        """Shop name printed on top of every label.

        System parameter ``cs_product_label_56x25.shop_name``; when it does not
        exist, ``Bebemálaga``. A blank value hides the line.
        """
        value = self.env['ir.config_parameter'].sudo().get_param(SHOP_NAME_PARAM, SHOP_NAME_DEFAULT)
        return (value or '').strip()

    @api.model
    def _normalize_data(self, data):
        """Report data normally travels as JSON (string keys); accept int keys too."""
        qty = data.get('quantity_by_product') or {}
        return {**data, 'quantity_by_product': {str(k): v for k, v in qty.items()}}

    @api.model
    def _label_name(self, product):
        """Product name, without reference nor variant (the variant gets its own line).

        Names imported from WooCommerce sometimes carry HTML entities
        (``Molis&amp;Co``); they are decoded here so QWeb escapes them once.
        """
        return html.unescape(product.name or '')

    @api.model
    def _label_variant(self, product):
        """Attribute values of a variant, e.g. ``Rojo, 0-6 meses``; empty for templates."""
        if product._name != 'product.product':
            return ''
        return html.unescape(product.product_template_attribute_value_ids._get_combination_name() or '')
