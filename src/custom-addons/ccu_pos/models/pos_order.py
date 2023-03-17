from itertools import groupby
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from operator import itemgetter


class PosOrder(models.Model):
    _name = 'pos.order'
    _description = 'Point of Sale Order'
    _inherit = ['pos.order']

    account_moves = fields.One2many('account.move', 'pos_order_id', string="Account moves")
    account_moves_count = fields.Integer('Number of account moves', compute= '_compute_account_moves_count')

    def _compute_account_moves_count(self):
        for rec in self:
            account_moves_count = self.env['account.move'].search_count([('pos_order_id', '=', rec.id)])
            rec.account_moves_count = account_moves_count

    def _default_sequence_prefix(self):
        if self.session_id.config_id.sequence_id.prefix:
            return self.session_id.config_id.sequence_id.prefix.strip('/')
        return False

    sequence_prefix = fields.Char("Cashier Prefix", compute='_compute_sequence_prefix', store=True,
                                  default=_default_sequence_prefix)

    @api.depends('session_id')
    def _compute_sequence_prefix(self):
        for rec in self:
            rec.sequence_prefix = rec._default_sequence_prefix()

    def _prepare_invoice_vals(self):
        vals = super(PosOrder, self)._prepare_invoice_vals()
        vals['pos_order_id'] = self.id
        vals['pos_session_id'] = self.session_id.id
        vals['printer_code'] = self.session_id.config_id.printer_code or ''
        if self.session_id:
            address_partner = self.session_id.config_id.picking_type_id.warehouse_id.partner_id
        else:
            address_partner = self.company_id.partner_id
        vals['departure_address'] = "%s - %s" % (address_partner.street, address_partner.street2 or '',)
        vals['departure_city'] = address_partner.city
        vals['departure_state'] = address_partner.state_id.name

        return vals

    def reset_cashier_prefix(self):
        moves = self.env['pos.order'].search([])
        moves._compute_sequence_prefix()

    def group_account_move_lines(self, move_vals):
        list_of_lines = [line[2] for line in move_vals['invoice_line_ids']]
        list_of_lines.sort(key=itemgetter('principal_company'))
        grouped_lines = []
        for method, items in groupby(list_of_lines, key=itemgetter('principal_company')):
            grouped_lines.append(list(items))
        list_of_move_vals = []
        for lines in grouped_lines:
            move_vals['invoice_line_ids'] = [(0, 0, line) for line in lines]
            list_of_move_vals.append(move_vals.copy())
        return list_of_move_vals

    def action_pos_order_invoice(self):
        moves = self.env['account.move']

        for order in self:
            # Force company for all SUPERUSER_ID action
            if order.account_move:
                moves += order.account_move
                continue

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))
            account_move_vals = order._prepare_invoice_vals()
            # group account_moves by principal_company
            account_moves = self.group_account_move_lines(account_move_vals)
            for move_vals in account_moves:
                new_move = moves.sudo().with_company(order.company_id)\
                                .with_context(default_move_type=move_vals['move_type'])\
                                .create(move_vals)
                message = _("This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
                new_move.message_post(body=message)
                new_move.sudo().with_company(order.company_id)._post()
                # we call _compute_remain to recalculate the last caf used to then correctly assign the invoice name
                caf = self.env['l10n_cl.dte.caf'].search([('l10n_latam_document_type_id', '=', new_move.l10n_latam_document_type_id.id)])
                caf._compute_remain()
                moves += new_move
            order.write({'account_moves': [(6, 0, [move.id for move in moves])], 'state': 'invoiced'})

        if not moves:
            return {}

        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': moves and moves.ids[0] or False,
        }

    def action_account_moves(self):
        return {
            'name': _('Pos order invoices'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('pos_order_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def _prepare_invoice_line(self, order_line):
        return {
            'product_id': order_line.product_id.id,
            'quantity': order_line.qty if self.amount_total >= 0 else -order_line.qty,
            'discount': order_line.discount,
            'price_unit': order_line.price_unit,
            'principal_company': order_line.product_id.principal_company,
            'name': order_line.product_id.display_name,
            'tax_ids': [(6, 0, order_line.tax_ids_after_fiscal_position.ids)],
            'product_uom_id': order_line.product_uom_id.id,
        }
