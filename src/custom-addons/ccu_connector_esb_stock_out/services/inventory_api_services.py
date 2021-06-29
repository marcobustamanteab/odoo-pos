from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component

class InventoryApiService(Component):
    _inherit = "base.rest.service"
    _name = "inventory.api.service"
    _usage = "inventory"
    _collection = "base.rest.inventory.api.services"
    _description = """
        Partner New API Services
        Services developed with the new api provided by base_rest
    """

    @restapi.method(
        [(["/", "/update_sync"], "POST")],
        input_param=Datamodel("picking.put.request"),
        output_param=Datamodel("picking.put.response"),
        auth="public",
    )
    def update_sync(self, picking_put_request):
        res = []
        picking_put_response = self.env.datamodels["picking.put.response"]
        if picking_put_request.sync_uuid:
            picking = self.env['stock.picking'].sudo().search([('sync_uuid', '=', picking_put_request.sync_uuid)],
                                                              limit=1)
            if len(picking) == 1:
                message = "status: " + picking_put_request.status + "- text: " + picking_put_request.text
                status = picking_put_request.status
                #picking.sudo().with_delay(channel='root.picking').update_sync(status, message)
                picking.sudo().update_sync(status, message)
                res = picking_put_response(code=1, message='OK')
            else:
                res = picking_put_response(code=-1, message='Picking not found!')
        else:
            res = picking_put_response(code=-1, message='stock_picking_id is required!')
        return res

