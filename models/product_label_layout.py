import logging

from odoo import api, fields, models

from .constants import LABEL_FORMAT, LABEL_FORMAT_NAME, PRICELIST_PARAM, REPORT_XMLID

_logger = logging.getLogger(__name__)


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    print_format = fields.Selection(
        selection_add=[(LABEL_FORMAT, LABEL_FORMAT_NAME)],
        ondelete={LABEL_FORMAT: 'set default'},
        default=LABEL_FORMAT,
    )
    pricelist_id = fields.Many2one(default=lambda self: self._default_label_pricelist())

    @api.model
    def _default_label_pricelist(self):
        """Pricelist used for label prices.

        1. ``cs_product_label_56x25.pricelist_id`` system parameter, if it points
           to an existing pricelist.
        2. Otherwise, the pricelist Odoo would apply to the current user
           (same resolution as the website / sale order fallback).
        """
        Pricelist = self.env['product.pricelist']
        raw = self.env['ir.config_parameter'].sudo().get_param(PRICELIST_PARAM)
        if raw:
            try:
                pricelist = Pricelist.browse(int(raw)).exists()
            except ValueError:
                pricelist = Pricelist
                _logger.warning("Invalid value %r for system parameter %s", raw, PRICELIST_PARAM)
            if pricelist:
                return pricelist
        partner = self.env.user.partner_id
        return Pricelist._get_partner_pricelist_multi([partner.id]).get(partner.id, Pricelist)

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()
        if self.print_format == LABEL_FORMAT:
            xml_id = REPORT_XMLID
            data = {**data, 'price_included': True}
        return xml_id, data
