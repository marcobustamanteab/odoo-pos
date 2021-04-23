from datetime import datetime
from unittest.mock import MagicMock

from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.tests import tagged

from ..models.res_partner import PartnerGender


@tagged('post_install')
class TestLabarraPartner(common.TransactionCase):
    def setUp(self):
        super(TestLabarraPartner, self).setUp()
        self.partner_params = {
            'email': 'test@labarra.cl',
            'name': 'Example Partner',
            'vat': '9061768-0',
            'dob': datetime.strptime('1993-11-29', "%Y-%m-%d"),
            'gender': PartnerGender.MALE,
            'mobile': '+56993231837',
            'street': 'Av. Las Condes 10333',
            'category': 'copero'
        }

    def test_create__with_age_less_than_18__should_raise_validation_error(self):
        # Arrange
        self.partner_params.pop('dob')
        ten_year_old_dob = datetime.now() - relativedelta(years=10)
        self.partner_params['dob'] = ten_year_old_dob

        # Assert
        with self.assertRaises(ValidationError):
            # Act
            self.env['res.partner'].create(self.partner_params)

    def test_create__with_age_more_than_120__should_raise_validation_error(self):
        # Arrange
        self.partner_params.pop('dob')
        hundred_and_thirty_year_old_dob = datetime.now() + relativedelta(years=130)
        self.partner_params['dob'] = hundred_and_thirty_year_old_dob

        # Assert
        with self.assertRaises(ValidationError):
            # Act
            self.env['res.partner'].create(self.partner_params)

    def test_create__with_invalid_email__should_raise_validation_error(self):
        # Arrange
        invalid_email = "this_is_not_an_email"
        self.partner_params['email'] = invalid_email

        # Assert
        with self.assertRaises(ValidationError):
            # Act
            self.env['res.partner'].create(self.partner_params)

    def test_create__with_vat_longer_than_12_chars__should_raise_validation_error(self):
        # Arrange
        invalid_vat = "1111111111111111111111111111111111"
        self.partner_params['vat'] = invalid_vat

        # Assert
        with self.assertRaises(ValidationError):
            # Act
            self.env['res.partner'].create(self.partner_params)

    def test_create__with_invalid_verification_digit_vat__should_raise_validation_error(self):
        # Arrange
        invalid_vdig_vat = "18636959-1"
        self.partner_params['vat'] = invalid_vdig_vat

        # Assert
        with self.assertRaises(ValidationError):
            # Act
            self.env['res.partner'].create(self.partner_params)

    def test_update_category__with_new_category__should_update_partners_category_to_new_category(self):
        # Arrange
        partner = self.env['res.partner'].create(self.partner_params)
        partner.category = 'copero'
        new_category = 'bartender'
        partner._calculate_category = MagicMock(return_value=new_category)

        expected_new_category = 'bartender'

        # Act
        partner.update_category()

        # Assert
        self.assertEqual(expected_new_category, partner.category)

    def test_update_category__with_new_category__should_call__update_pricelist_method(self):
        # Arrange
        partner = self.env['res.partner'].create(self.partner_params)
        partner.category = 'copero'
        new_category = 'bartender'
        partner._calculate_category = MagicMock(return_value=new_category)
        partner._update_pricelist = MagicMock()

        expected_calls = 1

        # Act
        partner.update_category()

        # Assert
        self.assertEqual(expected_calls, partner._update_pricelist.call_count)

    def test_update_category__with_same_category__should_not_call__update_pricelist_method(self):
        # Arrange
        partner = self.env['res.partner'].create(self.partner_params)
        partner.category = 'copero'
        same_category = 'copero'
        partner._calculate_category = MagicMock(return_value=same_category)
        partner._update_pricelist = MagicMock()

        # Act
        partner.update_category()

        # Assert
        partner._update_pricelist.assert_not_called()
