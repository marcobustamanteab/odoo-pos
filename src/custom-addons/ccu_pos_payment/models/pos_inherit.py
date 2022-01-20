# -*- coding: utf-8 -*-
from itertools import groupby
from datetime import datetime, timedelta, date
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):

	_inherit = "pos.order"

	def _process_payment_lines(self, pos_order, order, pos_session, draft):
		prec_acc = order.pricelist_id.currency_id.decimal_places
		order_bank_statement_lines= self.env['pos.payment'].search([('pos_order_id', '=', order.id)])
		order_bank_statement_lines.unlink()
		for payments in pos_order['statement_ids']:
			if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):
				order.add_payment(self._payment_fields(order, payments[2], pos_order))
		order.amount_paid = sum(order.payment_ids.mapped('amount'))
		if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
			cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
			if not cash_payment_method:
				raise UserError(_("No se encontró ningún estado de caja para esta sesión. No se puede registrar el efectivo devuelto."))
			return_payment_vals = {
				'name': _('return'),
				'pos_order_id': order.id,
				'amount': -pos_order['amount_return'],
				'payment_date': fields.Date.context_today(self),
				'payment_method_id': cash_payment_method.id,
				'cheque_owner_name' : pos_order.get('owner_name') or '',
				'check_date' : pos_order.get('check_date'),
				'cheque_number' : pos_order.get('cheque_number'),
			}
			order.add_payment(return_payment_vals)

	def _payment_fields(self, order, ui_paymentline, pos_order):
		payment_date = ui_paymentline['name']
		payment_date = fields.Date.context_today(self, fields.Datetime.from_string(payment_date))
		payment_method = self.env['pos.payment.method'].browse(ui_paymentline['payment_method_id'])
		if payment_method.cheque_information == True:
			if not pos_order.get('check_date'):
				raise UserError(_("Por Favor Ingresar Fecha de Transferencia"))
			if not pos_order.get('owner_name'):
				raise UserError(_("Por Favor Ingresar Nombre de Transferencia"))
			if not pos_order.get('vat'):
				raise UserError(_("Por Favor Ingresar RUT de Transferencia"))
			self.check_vat(pos_order.get('vat'))
			return {
				'amount': ui_paymentline['amount'] or 0.0,
				'payment_date': payment_date,
				'payment_method_id': ui_paymentline['payment_method_id'],
				'card_type': ui_paymentline.get('card_type'),
				'transaction_id': ui_paymentline.get('transaction_id'),
				'pos_order_id': order.id,
				'vat' : pos_order.get('vat'),
				'cheque_owner_name' : pos_order.get('owner_name'),
				'check_date' : pos_order.get('check_date'),
				'cheque_number' : pos_order.get('cheque_number'),
			}
		else:
			return {
				'amount': ui_paymentline['amount'] or 0.0,
				'payment_date': payment_date,
				'payment_method_id': ui_paymentline['payment_method_id'],
				'card_type': ui_paymentline.get('card_type'),
				'transaction_id': ui_paymentline.get('transaction_id'),
				'pos_order_id': order.id,
			}

	def check_vat(self, vat):
		if vat:
			if len(vat) > 12:
				raise UserError(_("El RUT debe contener menos caracteres."))
			vat_raw = vat.replace('.', '').replace('-', '')
			body, vdig = vat_raw[:-1], vat_raw[-1].upper()
			try:
				vali = list(range(2, 8)) + [2, 3]
				operar = "0123456789K0"[11 - (sum([int(digit) * factor for digit, factor in zip(body[::-1], vali)]) % 11)]
				if operar != vdig:
					raise UserError(_("RUT No Válido."))
			except IndexError:
				raise UserError(_("RUT No Válido."))



class PosConfigInherit(models.Model):

	_inherit = "pos.config"

	cheque_information = fields.Boolean(string="Agregue Información del Pago")


class PosOrderInherit(models.Model):

	_inherit = "pos.payment"

	vat = fields.Char(string="Rut")
	cheque_owner_name = fields.Char(string="Nombre del Cliente")
	check_date = fields.Date(string="Fecha", default=lambda self: str(datetime.now()))
	cheque_number = fields.Char(string="Referencia")

class AccountJournal(models.Model):

	_inherit = "pos.payment.method"

	cheque_information = fields.Boolean(string="Agregue Información del Pago")
