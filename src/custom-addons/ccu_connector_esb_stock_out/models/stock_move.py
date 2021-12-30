from odoo import api, models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    is_sync = fields.Boolean(string='Synchronize', compute="_compute_is_sync", store=True)
    sync_uuid = fields.Char(string='Sync. UUID', compute="_compute_is_sync", store=True)
    posted_payload = fields.Text('Posted Payload', compute="_compute_is_sync", store=True)
    sync_text = fields.Text(string='Sync. Text', compute="_compute_is_sync", store=True)

    @api.depends('picking_id.is_sync','picking_id.sync_uuid','picking_id.posted_payload','picking_id.sync_reference')
    def _compute_is_sync(self):
        for rec in self:
            rec.is_sync = rec.picking_id.is_sync
            rec.sync_uuid = rec.picking_id.sync_uuid
            rec.posted_payload = rec.picking_id.posted_payload
            rec.sync_text = rec.picking_id.sync_text
