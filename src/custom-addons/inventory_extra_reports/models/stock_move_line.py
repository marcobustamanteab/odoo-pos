from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    ccu_deptid = fields.Char(string='Departamento', related='move_id.company_id.esb_default_analytic_id.code', store=True)
    ccu_sentido = fields.Char(string='Sentido', related='move_id.picking_type_id.ccu_code_usage', store=True)
    ccu_ps_code = fields.Char(string='PS Code', related='product_id.code_peoplesoft', store=True)
    ccu_ps_code_active = fields.Boolean(string='Producto Activo?', related='product_id.active', store=True)
    ccu_bu = fields.Char(string='Business Unit', compute='_get_bu', store=True)
    ccu_origen = fields.Char(compute='_get_origen', string="Origen", store=True)

    @api.one
    def _get_bu(self):
        self.ccu_bu = self.move_id.location_id.ccu_code or self.move_id.location_dest_id.ccu_code

    @api.one
    def _get_origen(self):
        self.ccu_origen = ''
        code_bu = self.move_id.location_id.ccu_code or self.move_id.location_dest_id.ccu_code
        if code_bu:
            if self.product_id.code_peoplesoft and self.product_id.type == 'product':
                # Ask for incoming or outgoing + type of client or type of sale
                sale_order = self.env['sale.order'].search([('name', '=', self.move_id.origin)], limit=1)
                if self.move_id.picking_type_id.ccu_code_usage == "EX":
                    if sale_order.type_id.no_charge_accounting:
                        self.ccu_origen = self.product_id.categ_id.outgoing_code_no_charge
                    elif self.move_id.partner_id.commercial_partner_id.client_type == 'RELACIONADA':
                        self.ccu_origen = self.product_id.categ_id.outgoing_code_related
                    elif self.move_id.partner_id.commercial_partner_id.client_type == 'FILIAL':
                        self.ccu_origen = self.product_id.categ_id.outgoing_code_subsidiary
                        # TODO: Substandard Mapping
                        # outgoing_code_substandard = fields.Char(string='Substandard Out Code', size=2)
                    else:
                        self.ccu_origen = self.product_id.categ_id.outgoing_code

                else:
                    # When Return to Branch we dont have the Partner Name
                    if self.move_id.partner_id:
                        if self.move_id.partner_id.commercial_partner_id.client_type == 'RELACIONADA':
                            self.ccu_origen = self.product_id.categ_id.incoming_code_related
                        elif self.move_id.partner_id.commercial_partner_id.client_type == 'FILIAL':
                            self.ccu_origen = self.product_id.categ_id.incoming_code_subsidiary
                            # TODO: Substandard Mapping
                            # incoming_code_substandard = fields.Char(string='Substandard Out Code', size=2)
                        else:
                            self.ccu_origen = self.product_id.categ_id.incoming_code
                    else:
                        self.ccu_origen = self.product_id.categ_id.incoming_code
