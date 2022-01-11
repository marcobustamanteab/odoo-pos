# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)



class AccountMoveLine(models.Model):

	_inherit = "account.move.line"

	vat = fields.Char(string="Rut", compute='_get_payment_refs',store=True, readonly=False)
	cheque_owner_name = fields.Char(string="Nombre del Cliente", compute='_get_payment_refs',store=True, readonly=False)
	check_date = fields.Date(string="Fecha", compute='_get_payment_refs',store=True, readonly=False)
	cheque_number = fields.Char(string="Referencia", compute='_get_payment_refs',store=True, readonly=False)

	@api.depends('move_id.line_ids', 'move_id.line_ids.debit', 'move_id.line_ids.credit')
	def _get_payment_refs(self):
		for rec in self:
			pos_order_id = False
			if rec.pos_order_id:
				order_payment_lines = self.env['pos.payment'].search([('pos_order_id', '=', rec.pos_order_id.id),('amount','=',rec.debit),('vat','!=','')],limit=1)
				if order_payment_lines:
					rec.vat = order_payment_lines.vat
					rec.cheque_owner_name = order_payment_lines.cheque_owner_name
					rec.check_date = order_payment_lines.check_date
					rec.cheque_number = order_payment_lines.cheque_number
