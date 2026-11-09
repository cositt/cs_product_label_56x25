from odoo.tests import TransactionCase, tagged

LABEL_FORMAT = 'cs_56_25'
REPORT_XMLID = 'cs_product_label_56x25.report_product_label_56x25'
PRICELIST_PARAM = 'cs_product_label_56x25.pricelist_id'
SHOP_NAME_PARAM = 'cs_product_label_56x25.shop_name'


@tagged('post_install', '-at_install')
class TestLabel56x25(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref('product.group_product_pricelist')
        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'Retail test',
            'sequence': 1,
        })
        color = cls.env['product.attribute'].create({
            'name': 'Color',
            'value_ids': [(0, 0, {'name': 'Rojo'}), (0, 0, {'name': 'Azul'})],
        })
        cls.template = cls.env['product.template'].create({
            'name': 'Calcetines Molis&amp;Co',
            'list_price': 1.0,
            'is_storable': True,
            'attribute_line_ids': [(0, 0, {
                'attribute_id': color.id,
                'value_ids': [(6, 0, color.value_ids.ids)],
            })],
        })
        cls.red, cls.blue = cls.template.product_variant_ids
        cls.red.write({'barcode': '8436579283780', 'default_code': 'CAL-R'})
        cls.blue.write({'default_code': 'CAL-A'})
        cls.env['product.pricelist.item'].create([{
            'pricelist_id': cls.pricelist.id,
            'applied_on': '0_product_variant',
            'product_id': cls.red.id,
            'compute_price': 'fixed',
            'fixed_price': 36.95,
        }, {
            'pricelist_id': cls.pricelist.id,
            'applied_on': '0_product_variant',
            'product_id': cls.blue.id,
            'compute_price': 'fixed',
            'fixed_price': 39.95,
        }])

    def _wizard(self, **vals):
        vals.setdefault('product_ids', [(6, 0, (self.red | self.blue).ids)])
        return self.env['product.label.layout'].create(vals)

    def _render(self, wizard):
        xml_id, data = wizard._prepare_report_data()
        report = self.env.ref(xml_id)
        html, _ = report._render_qweb_html(xml_id, docids=None, data=data)
        return html.decode()

    # --- format and report action ------------------------------------------
    def test_format_is_default_and_uses_own_report(self):
        wizard = self._wizard(pricelist_id=self.pricelist.id)
        self.assertEqual(wizard.print_format, LABEL_FORMAT)
        xml_id, data = wizard._prepare_report_data()
        self.assertEqual(xml_id, REPORT_XMLID)
        self.assertTrue(data['price_included'])

    def test_paperformat_is_56x25(self):
        paper = self.env.ref(REPORT_XMLID).paperformat_id
        self.assertEqual((paper.page_height, paper.page_width), (56, 25))
        self.assertEqual(paper.orientation, 'Landscape')
        self.assertEqual((paper.margin_top, paper.margin_bottom,
                          paper.margin_left, paper.margin_right), (0, 0, 0, 0))

    def test_other_formats_untouched(self):
        xml_id, _ = self._wizard(print_format='dymo')._prepare_report_data()
        self.assertEqual(xml_id, 'product.report_product_template_label_dymo')
        xml_id, _ = self._wizard(print_format='2x7xprice')._prepare_report_data()
        self.assertEqual(xml_id, 'product.report_product_template_label_2x7')
        xml_id, _ = self._wizard(print_format='zplxprice')._prepare_report_data()
        self.assertEqual(xml_id, 'stock.label_product_product')

    def test_picking_type_accepts_format(self):
        picking_type = self.env.ref('stock.picking_type_in')
        picking_type.product_label_format = LABEL_FORMAT
        self.assertEqual(picking_type.product_label_format, LABEL_FORMAT)

    # --- default pricelist ---------------------------------------------------
    def test_default_pricelist_from_param(self):
        self.env['ir.config_parameter'].sudo().set_param(PRICELIST_PARAM, str(self.pricelist.id))
        self.assertEqual(self._wizard().pricelist_id, self.pricelist)

    def test_default_pricelist_ignores_bad_param(self):
        self.env['ir.config_parameter'].sudo().set_param(PRICELIST_PARAM, 'basura')
        wizard = self._wizard()
        expected = self.env['product.pricelist']._get_partner_pricelist_multi(
            [self.env.user.partner_id.id])[self.env.user.partner_id.id]
        self.assertEqual(wizard.pricelist_id, expected)

    def test_default_pricelist_falls_back_to_partner_pricelist(self):
        self.env['ir.config_parameter'].sudo().set_param(PRICELIST_PARAM, '')
        partner = self.env.user.partner_id
        expected = self.env['product.pricelist']._get_partner_pricelist_multi([partner.id])[partner.id]
        self.assertEqual(self._wizard().pricelist_id, expected)

    # --- rendered content ----------------------------------------------------
    def test_render_variant_prices_names_and_barcodes(self):
        html = self._render(self._wizard(pricelist_id=self.pricelist.id, custom_quantity=2))
        self.assertIn('36,95', html.replace('.', ','))
        self.assertIn('39,95', html.replace('.', ','))
        self.assertNotIn('1,00', html.replace('.', ','))
        self.assertIn('Molis&amp;Co', html)          # single escape: prints "Molis&Co"
        self.assertNotIn('&amp;amp;', html)
        self.assertIn('CAL-R', html)
        self.assertIn('<div class="cs_label_variant">Rojo</div>', html)
        self.assertIn('<div class="cs_label_variant">Azul</div>', html)
        self.assertNotIn('(Rojo)', html)            # not glued to the (truncated) name
        self.assertIn('CAL-A', html)
        self.assertEqual(html.count('class="cs_label"'), 4)
        # only the red variant has a barcode
        self.assertEqual(html.count('class="cs_label_barcode"'), 2)
        self.assertIn('8436579283780', html)

    def test_render_from_receipt_quantities(self):
        receipt = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'move_ids': [(0, 0, {
                'product_id': self.red.id,
                'product_uom_qty': 3,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            })],
        })
        receipt.action_confirm()
        action = receipt.action_open_label_layout()
        wizard = self.env['product.label.layout'].with_context(action['context']).create({
            'pricelist_id': self.pricelist.id,
        })
        self.assertEqual(wizard.print_format, LABEL_FORMAT)
        html = self._render(wizard)
        self.assertEqual(html.count('class="cs_label"'), 3)

    def test_render_without_wizard_does_not_crash(self):
        report = self.env.ref(REPORT_XMLID)
        html, _ = report._render_qweb_html(REPORT_XMLID, docids=None, data={
            'active_model': 'product.product', 'quantity_by_product': {}, 'layout_wizard': 0})
        self.assertNotIn('class="cs_label"', html.decode())

    # --- shop name header (INC-002) ----------------------------------------
    def test_render_shop_name_default(self):
        html = self._render(self._wizard(pricelist_id=self.pricelist.id))
        self.assertEqual(html.count('class="cs_label_shop"'), 2)
        self.assertIn('<div class="cs_label_shop">Bebemálaga</div>', html)

    def test_render_shop_name_from_param(self):
        self.env['ir.config_parameter'].sudo().set_param(SHOP_NAME_PARAM, 'Tienda Test')
        html = self._render(self._wizard(pricelist_id=self.pricelist.id))
        self.assertIn('<div class="cs_label_shop">Tienda Test</div>', html)
        self.assertNotIn('Bebemálaga', html)

    def test_render_shop_name_param_blank_hides_header(self):
        self.env['ir.config_parameter'].sudo().set_param(SHOP_NAME_PARAM, ' ')
        html = self._render(self._wizard(pricelist_id=self.pricelist.id))
        self.assertNotIn('class="cs_label_shop"', html)

    def test_label_box_sizing_for_wkhtmltopdf(self):
        """wkhtmltopdf (old WebKit) only honours the prefixed property; without it the
        2 mm side padding is added to the 56 mm width and the price overflows the edge."""
        html = self._render(self._wizard(pricelist_id=self.pricelist.id))
        self.assertIn('-webkit-box-sizing: border-box', html)

    def test_report_body_margins_are_reset(self):
        """Body and Bootstrap container margins would push the label off the 56 mm page."""
        html = self._render(self._wizard(pricelist_id=self.pricelist.id))
        self.assertIn('html, body, .container, .article, .cs_label_page {', html)
