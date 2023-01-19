# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import re
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import ValidationError

CustomerPortal.OPTIONAL_BILLING_FIELDS.extend(['dob', 'gender'])


class LaBarraCategory:
    COPERO = "copero"
    CATADOR = "catador"
    BARTENDER = "bartender"
    VIP = "vip"
    VIP_PREMIUM = "vip-premium"

class LaBarraProductPricelist:
    COPERO = "pricelist_copero"
    CATADOR = 'pricelist_catador'
    BARTENDER = "pricelist_bartender"
    VIP = "pricelist_vip"
    VIP_PREMIUM = "pricelist_vip_premium"

class PartnerGender:
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNSPECIFIED = "unspecified"


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Extended Fields
    email = fields.Char(required=True)
    mobile = fields.Char(required=True)
    name = fields.Char(required=True)
    street = fields.Char(required=True)
    vat = fields.Char(required=True)

    # New Fields
    over_limit_purchase = fields.Boolean('Over-limit purchase authorization')
    gender = fields.Selection([
        (PartnerGender.MALE, 'Hombre'),
        (PartnerGender.FEMALE, 'Mujer'),
        (PartnerGender.OTHER, 'Otro'),
        (PartnerGender.UNSPECIFIED, 'Prefiero no Decirlo')],
        string='Gender', default=PartnerGender.MALE, help="Gender", required=True)
    
    category = fields.Selection([
        (LaBarraCategory.CATADOR, 'Catador'),
        (LaBarraCategory.COPERO, 'Copero'),
        (LaBarraCategory.BARTENDER, 'Bartender'),
        (LaBarraCategory.VIP, 'VIP'),
        (LaBarraCategory.VIP_PREMIUM, 'VIP - Premium')],
        string='Category', default=LaBarraCategory.COPERO, help="Category", required=True)

    ##### TODO: The status 'bloqued' is wrong the correct is 'locked'. MSP
    status = fields.Selection(
        string='Ecommerce status',
        selection=[
            ('unconfirmed', 'Unconfirmed'),
            ('active', 'Active'),
            ('locked', 'Locked'),
        ],
        default = 'unconfirmed',
        required = True
    )

    dob = fields.Date(string='Date of Birth', help="Date of Birth", required=True)
    age = fields.Integer(string="Age")

    limit_purchase = fields.Float(string="Limit Purchase", default=500000)
    monthly_purchase = fields.Float(string="Monthly Purchase")
    reached_limit = fields.Boolean(string="Reached Limit")
    is_employee = fields.Boolean(string="Is Employee", default=False)
    distribution_center = fields.Many2one(
        'res.partner.distribution_center', string="Distribution Center")

    @api.constrains('vat')
    def check_vat(self):
        for record in self:
            if record.vat:
                if len(record.vat) > 12:
                    raise ValidationError(_("El RUT debe tener máximo 12 caracteres."))
                vat_raw = record.vat.replace('.', '').replace('-', '')
                body, vdig = vat_raw[:-1], vat_raw[-1].upper()
                try:
                    vali = list(range(2, 8)) + [2, 3]
                    operar = "0123456789K0"[
                        11 - (sum([int(digit) * factor
                                   for digit, factor in
                                   zip(body[::-1], vali)]) % 11)]
                    if operar != vdig:
                        raise ValidationError(_("El RUT ingresado no es válido."))
                except IndexError:
                    raise ValidationError(_("El RUT ingresado no es válido."))

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and not self._is_valid_email(record.email):
                raise ValidationError(_("El correo electrónico ingresado no presenta un formato válido."))
        return True

    @api.constrains('dob')
    def _check_dob(self):
        for record in self:
            if record.dob and not self._is_valid_age(record.dob):
                raise ValidationError(_("La edad requerida para el registro es entre 18 y 120 años."))
        return True

    @api.onchange('dob')
    def _onchange_dob(self):
        """Updates age field when dob is changed"""
        for record in self:
            if record.dob:
                record.age = self._calculate_age(record.dob)

    @api.onchange('vat')
    def _onchange_vat(self):
        """Updates is_employee field when vat is changed"""
        for record in self:
            if record.vat:
                vat_raw = record.vat.replace('.', '').replace('-', '')
                record.is_employee = self._check_if_vat_present_in_employee_database(vat_raw)

    @api.onchange('is_employee')
    def _onchange_is_employee(self):
        """Clear distribution center and address fields when is_employee=False"""
        for record in self:
            if not record.is_employee:
                if record.distribution_center:
                    record.distribution_center = None
                    record.street = ""
                    record.street2 = ""
                    record.city_id = None
                    record.city = ""
                    record.state_id = None
                    record.country_id = None
                    record.zip = ""

    @api.onchange('distribution_center')
    def _onchange_distribution_center(self):
        """Updates address fields when distribution center is changed"""
        for record in self:
            if record.distribution_center:
                record.street = record.distribution_center.street
                street_number = record.distribution_center.street_number
                record.street = record.street + " " + street_number if street_number else record.street
                record.street2 = ""

                city = self.env['res.city'].search([('name', '=ilike', record.distribution_center.city_name)], limit=1)
                if city:
                    # city, state and country will be set automatically based on city_id
                    record.city_id = city.id
                else:
                    record.city = record.distribution_center.city_name
                    record.state_id = None
                    record.country_id = self.env['res.country'].search([('name', '=', "Chile")], limit=1).id
                record.zip = ""

    def _update_pricelist(self, record):
        category_to_pricelist = {LaBarraCategory.COPERO: LaBarraProductPricelist.COPERO,
                                 LaBarraCategory.CATADOR: LaBarraProductPricelist.CATADOR,
                                 LaBarraCategory.BARTENDER: LaBarraProductPricelist.BARTENDER,
                                 LaBarraCategory.VIP: LaBarraProductPricelist.VIP,
                                 LaBarraCategory.VIP_PREMIUM: LaBarraProductPricelist.VIP_PREMIUM}
        pricelist_name = category_to_pricelist[record.category]

        pricelist_id = self.env['ir.model.data'].search([('model', '=', 'product.pricelist'),
                                                         ('name', '=', pricelist_name)], limit=1).res_id

        record.property_product_pricelist = pricelist_id

    @staticmethod
    def _is_valid_email(email):
        email_regex = '^[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}$'
        return re.search(email_regex, email)

    def _is_valid_age(self, dob):
        return 18 <= self._calculate_age(dob) <= 120

    @staticmethod
    def _calculate_age(dob):
        current_date = datetime.now()
        return relativedelta(current_date, dob).years

    @staticmethod
    def _check_if_vat_present_in_employee_database(vat):
        # This simulates an external API call for crossing the given VAT with the HR employee database
        employee_vat_list = ['186369599']
        return vat in employee_vat_list

    def _calculate_category(self):
        # If is_employee then the category should never change
        if self.is_employee:
            return self.category

        timespan_in_months = 6
        current_date = datetime.now()
        timespan_start = current_date - relativedelta(months=timespan_in_months)

        # TODO: create_date is not the "order placed" date (it's the cart creation date)
        orders = self.sale_order_ids.search([('create_date', '>=', timespan_start)])

        total_order_amount = sum(o.amount_total for o in orders)

        return self._get_category_based_on_amount(total_order_amount)

    @api.model
    def update_category(self):
        for record in self:
            new_category = self._calculate_category()
            if new_category != self.category:
                self.category = new_category

                # After every category update, pricelist should be updated too
                self._update_pricelist(record)

    @staticmethod
    def _get_category_based_on_amount(total_order_amount):
        first_upgrade = 200000
        second_upgrade = 300000

        if total_order_amount in range(0, first_upgrade):
            category = LaBarraCategory.COPERO
        elif total_order_amount in range(first_upgrade, second_upgrade):
            category = LaBarraCategory.CATADOR
        else:
            category = LaBarraCategory.BARTENDER

        return category

    @api.model
    def update_ages(self):
        """Updates age field for all partners (once a day)"""
        for rec in self.env['res.partner'].search([]):
            if rec.dob:
                rec.age = self._calculate_age(rec.dob)
    
    @api.model
    def update_limit_purchase(self):
        for rec in self:
            self.limitPurchase(rec)

    @api.onchange('category')
    def _onchange_category(self):
        """Updates property_product_pricelist and limit_purchase fields when category is changed"""
        for record in self:
            if record.category:
                self._update_pricelist(record)
                self.limitPurchase(record)

    def limitPurchase(self, rec):
        self.setLimitCategory(rec)
        # Check purchase amount to determine category placing
        if rec.category != LaBarraCategory.VIP_PREMIUM:
            self.updateMonthlyPurchase(rec)
            self.checkIfLimitReached(rec)
            
    def setLimitCategory(self, cat):
        if cat.category == LaBarraCategory.VIP:
            cat.limit_purchase = 200000
        elif cat.category in [LaBarraCategory.BARTENDER, LaBarraCategory.CATADOR, LaBarraCategory.COPERO]:
            cat.limit_purchase = 500000
        elif cat.category == LaBarraCategory.VIP_PREMIUM:
            cat.limit_purchase = 0
            cat.reached_limit = False

    def updateMonthlyPurchase(self, cat):
        current_date = datetime.now()
        first_day_month = datetime(current_date.year, current_date.month, 1, 0, 0, 0, 0)
        if cat._origin.id:
            orders = cat.env['sale.order'].search([('partner_id', '=', cat._origin.id),
                                                    ('create_date', '>=', first_day_month)])
            total_order_amount = sum(o.amount_total for o in orders)
            cat.monthly_purchase = total_order_amount
        else: 
            cat.monthly_purchase = 0
    
    def checkIfLimitReached(self, cat):
        cat.reached_limit = (cat.monthly_purchase >= cat.limit_purchase)

    @api.model
    def update_categories(self):
        """Updates category field for all non-employee partners (once a month)"""
        for partner in self.env['res.partner'].search([('is_employee', '=', False)]):
            partner.update_category()

    @api.model
    def validate_category_quantities(self, partner, products):
        res_partner = self.search([('id', '=', partner['id'])])
        today = datetime.today()
        weekday = datetime.now().weekday()
        monday = datetime.now() - timedelta(days=datetime.now().weekday())
        message = False
        if not res_partner.category_id:
            pass
        elif not res_partner.category_id.purchase_calendar or len(res_partner.category_id.purchase_calendar) != 7:
            message = _('No purchase calendar defined or incorrectly defined')
        elif res_partner.category_id.purchase_calendar[weekday] not in ['S', 's']:
            message = _('The customer cannot buy today.')
        elif res_partner.over_limit_purchase and not self.check_quantities(today, res_partner, products, res_partner.category_id.daily_exception_limit):
            message = _('Over daily exception limit.')
        elif not res_partner.over_limit_purchase and not self.check_quantities(today, res_partner, products, res_partner.category_id.daily_limit):
            message = _('Over daily limit.')
        elif not self.check_quantities(monday, res_partner, products, res_partner.category_id.weekly_limit):
            message = _('Over weekly limit.')
        return message

    def check_quantities(self, date_from, partner, products, limit):
        new_order_quantity = sum([product[0] for product in products])
        account_moves = self.env['account.move'].search([('move_type', '=', 'out_invoice'),
                                                         ('date', '>=', date_from),
                                                         ('partner_id', '=', partner.id)])
        total_quantity = 0
        for line in account_moves.invoice_line_ids:
            total_quantity += line.quantity
        if (new_order_quantity + total_quantity) > limit:
            return False
        return True

    @api.model
    def create(self, vals):
        category_id = vals.get('category_id')
        if category_id and len(category_id[0][-1]) > 1:
            raise ValidationError(_("You cannot create a contact with more than 1 category."))
        res = super().create(vals)
        return res

    def write(self, vals):
        if vals.get('category_id') and len(vals.get('category_id')[0][-1]) > 1:
            raise ValidationError(_("You cannot assign more than 1 category to a contact."))
        res = super().write(vals)
        return res

    @api.model
    def update_over_limit_purchase(self):
        for rec in self.search([('over_limit_purchase', '=', True)]):
            rec.over_limit_purchase = False
