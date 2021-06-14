from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel

class AccountMovePutRequest(Datamodel):
    _name = "account.move.put.request"

    sync_uuid = fields.String(required=True, allow_none=False)
    reference = fields.String(required=False, allow_none=False)