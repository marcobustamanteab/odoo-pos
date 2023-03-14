from odoo import api, fields, models, _


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
        # crear metodo para agrupar los movimientos por empresa mandante
        return [move_vals]

    def _generate_pos_order_invoice(self):
        moves = self.env['account.move']

        for order in self:
            if order.account_move:
                moves += order.account_move
                continue

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

            move_vals = order._prepare_invoice_vals()
            grouped_vals = self.group_account_move_lines(move_vals)
            for vals in grouped_vals:
                new_move = order._create_invoice(vals)
                new_move.sudo().with_company(order.company_id)._post()
                moves += new_move
            if moves:
                order.write({'account_move': moves[0].id, 'state': 'invoiced'})

        if not moves:
            return {}

        # cambiar respuesta
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
