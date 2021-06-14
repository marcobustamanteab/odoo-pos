from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component

class AccountApiService(Component):
    _inherit = "base.rest.service"
    _name = "account.api.service"
    _usage = "Account"
    _collection = "base.rest.account.api.services"
    _description = """
        Partner New API Services
        Services developed with the new api provided by base_rest
    """

    @restapi.method(
        [(["/", "/move/update_sync"], "POST")],
        input_param=Datamodel("account.move.put.request"),
        output_param=Datamodel("account.move.put.response"),
        auth="public",
    )
    def update_sync(self, account_move_put_request):
        """
                Search for partners
                :param partner_search_param: An instance of partner.search.param
                :return: List of partner.short.info
                """
        res = []
        account_move_put_response = self.env.datamodels["account.move.put.response"]
        if account_move_put_request.sync_uuid:
            account_move = self.env['account.move'].sudo().search(
                [('sync_uuid', '=', account_move_put_request.sync_uuid)], limit=1)
            if len(account_move) == 1:
                account_move.sudo().with_delay(channel='root.account').update_sync(account_move_put_request.reference)
                res = account_move_put_response(code=1, message='OK')
            else:
                res = account_move_put_response(code=-1, message='Move not found!')
        else:
            res = account_move_put_response(code=-1, message='sync_uuid is required!')
        return res

