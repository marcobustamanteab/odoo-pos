from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock

from odoo.tests import common
from odoo.tests import tagged

from ..models.res_partner import PartnerGender


@tagged('post_install')
class TestLabarraSaleOrder(common.TransactionCase):
    def setUp(self):
        super(TestLabarraSaleOrder, self).setUp()
        self.partner_params = {
            'email': 'test@labarra.cl',
            'name': 'Example Partner',
            'vat': '9061768-0',
            'dob': datetime.strptime('1993-11-29', "%Y-%m-%d"),
            'gender': PartnerGender.MALE,
            'mobile': '+56993231837',
            'street': 'Av. Las Condes 10333'
        }
        self.partner = self.env['res.partner'].create(self.partner_params)

        self.sale_order_params = {
            'amount_total': 100000,
            'partner_id': self.partner.id
        }
        self.sale_order = self.env['sale.order'].sudo().create(self.sale_order_params)

    def test_action_confirm__with_is_employee_as_true__should_not_call_partners_update_category_method(self):
        # Arrange
        partner = self.partner
        partner.is_employee = True
        partner.update_category = MagicMock()

        order = self.sale_order

        # Act
        with mock.patch.object(type(self.env['res.partner']), 'search') as mocked_search:
            mocked_search.return_value = partner
            order.action_confirm()

        partner.update_category.assert_not_called()

    def test_action_confirm__with_is_employee_as_false__should_call_partners_update_category_method_once(self):
        # Arrange
        partner = self.partner
        partner.is_employee = False
        partner.update_category = MagicMock()
        order = self.sale_order
        expected_calls = 1

        # Act
        with mock.patch.object(type(self.env['res.partner']), 'search') as mocked_search:
            mocked_search.return_value = partner
            order.action_confirm()

        # Assert
        self.assertEqual(expected_calls, partner.update_category.call_count)
