from odoo import api, fields, models, _


class AccountMove(models.Model):
    _name = 'account.move'
    _description = 'Account Move or Invoice'
    _inherit = ['account.move']

    def _default_sequence_prefix(self):
        if len(self.pos_order_ids) > 0:
            pos_order = self.pos_order_ids[0]
            prefix = pos_order.session_id.config_id.sequence_id.prefix
            return prefix.strip('/') if prefix else 'XXXX1'
        else:
            pos_session = self.env['pos.session'].search([('name', '=ilike', self.ref)])
            if pos_session:
                prefix = pos_session.config_id.sequence_id.prefix
                return prefix.strip('/') if prefix else 'XXXX2'
        return "XXXX3"

    pos_sequence_prefix = fields.Char("Cashier Prefix")
    pos_order_id = fields.Many2one('pos.order', string="POS Order")
    pos_session_id = fields.Many2one('pos.session', string="POS Session")
    printer_code = fields.Char("Printer Queue Code")

    departure_address = fields.Char("Departure Address")
    departure_city = fields.Char("Departure City")
    departure_state = fields.Char("Departure State")

    @api.onchange('company_id', 'pos_session_id', 'partner_id')
    def _onchange_departure_fields(self):
        for rec in self:
            if rec.pos_session_id:
                address_partner = rec.pos_session_id.config_id.picking_type_id.warehouse_id.partner_id
            else:
                address_partner = rec.company_id.partner_id
            rec.departure_address = "%s - %s" % (address_partner.street, address_partner.street2 or '',)
            rec.departure_city = address_partner.city
            rec.departure_state = address_partner.state_id.name

    def reset_cashier_prefix(self):
        moves = self.env['account.move'].search([])


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    pos_order_id = fields.Many2one('pos.order', string="POS Order")
    principal_company = fields.Many2one('res.company', string="Principal company")
