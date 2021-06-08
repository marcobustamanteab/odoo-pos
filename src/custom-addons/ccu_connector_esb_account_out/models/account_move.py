# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# Copyright (C) 2020 Konos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models
from odoo.addons.queue_job.job import job


class AccountMove(models.Model):
    _inherit = 'account.move'

    posted_payload = fields.Char('Posted Payload')

    @job
    def esb_send_account_move(self):
        self.ensure_one()
        payload_lines = []
        move_ref=self.name[-10:]
        if self.ref:
            move_ref=self.ref[-10:]
        considered_accounts_for_cc = ['210600'] # list of accounts that must have the analytic account for the integration
        distribution_center = self.env.user.default_branch_id.distribution_center if self.env.user.default_branch_id else "0"
        bank_deposit_analytic_account_id = False
        analytic_account_id = False
        if self.env['account.invoice'].search([('move_id', '=', self.id)]) and self.journal_id.code == 'DIFR':
            distribution_center = self.env['account.invoice'].search([('move_id', '=', self.id)]).branch_id.distribution_center
            analytic_account_id = self.env['account.invoice'].search([('move_id', '=', self.id)]).branch_id.analytic_account_id.code
            bank_deposit_analytic_account_id = self.env['account.invoice'].search([('move_id', '=', self.id)]).branch_id.bank_deposit_analytic_account_id.code
        elif self.env['account.invoice'].search([('move_id', '=', self.id)]):
            distribution_center = self.env['account.invoice'].search([('move_id', '=', self.id)]).branch_id.distribution_center
            analytic_account_id = self.env['account.invoice'].search([('move_id', '=', self.id)]).branch_id.analytic_account_id.code
        elif self.env['account.payment'].search([('move_name', '=', self.name)]) and self.journal_id.code == 'TRN': #all payments from Transbank must go to Santiago DC
            distribution_center = '033' # distribution center for Santiago
            analytic_account_id = '7A0000000' # Manantial generic analytic account
        elif self.env['account.payment'].search([('move_name', '=', self.name)]):
            distribution_center = self.env['account.payment'].search([('move_name', '=', self.name)]).branch_id.distribution_center or 0
            analytic_account_id = self.env['account.payment'].search([('move_name', '=', self.name)]).branch_id.analytic_account_id.code
            bank_deposit_analytic_account_id = self.env['account.payment'].search([('move_name', '=', self.name)]).branch_id.bank_deposit_analytic_account_id.code
        elif self.env['deposit.ticket'].search([('move_id', '=', self.id)]):
            bank_deposit_analytic_account_id = self.env['deposit.ticket'].search([('move_id', '=', self.id)]).branch_id.bank_deposit_analytic_account_id.code

        payload = {
            'account_move_name': self.name[-10:],
            'account_move_date': fields.Date.to_string(self.date),
            'account_move_ref': move_ref or '',
            'ccu_business_unit': self.company_id.ccu_business_unit,
            'ccu_business_unit_gl': self.company_id.ccu_business_unit,
            'doc_seq_nbr': distribution_center, #for the integration we decided to use the field doc_seq_nbr to send the CD number. That is a field that is not being used in Peoplesoft
            'account_move_line': payload_lines,
        }
        accounts = self.mapped('line_ids.account_id').filtered('ccu_sync')
        lines = [x for x in self.line_ids if x.account_id in accounts]
        for idx, line in enumerate(lines, start=1):
            base_currency = line.currency_id or line.company_currency_id
            base_amt = line.amount_currency or (line.debit - line.credit)
            line_currency = line.company_currency_id
            line_amt = (line.debit - line.credit)

            if line.analytic_account_id.code:
                analytic_code = line.analytic_account_id.code
            elif line.account_id.code == '110002' and bank_deposit_analytic_account_id:
                analytic_code = bank_deposit_analytic_account_id
            elif line.account_id.code not in considered_accounts_for_cc and analytic_account_id:
                analytic_code = analytic_account_id
            else:
                analytic_code = self.company_id.esb_default_analytic_id.code

            #analytic_code = (
            #    line.analytic_account_id.code or (if line.account_id.code == '11403' or )
            #    self.company_id.esb_default_analytic_id.code)

            payload_lines.append({
                "account_move_line_num": str(idx),
                "account_move_line_name": (
                    line.name or self.ref or self.name or '-')[:30],
                "account_move_line_account_code": line.account_id.code,
                "account_move_line_amount_base": str(int(base_amt)),
                "account_move_line_base_currency": base_currency.name or "",
                "account_move_line_analytic_code": analytic_code or "",
                "account_move_line_currency": line_currency.name or"",
                "account_move_line_amount": str(int(line_amt)),
                "account_move_line_tin": line.partner_id.vat or "",
            })
        esb_api_endpoint = '/AsientosContablesAPI'
        backend = self.company_id.backend_esb_id
        self.posted_payload = payload
        backend.api_esb_call("POST", esb_api_endpoint, payload)

    @api.multi
    def post(self, invoice=False):
        res = super(AccountMove, self).post(invoice)
        for move in self:
            if move.journal_id.type != 'bank' and move.journal_id.ccu_sync:
                move.with_delay().esb_send_account_move()
        return res
