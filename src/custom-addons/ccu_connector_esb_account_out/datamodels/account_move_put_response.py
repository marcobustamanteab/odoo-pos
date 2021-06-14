from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel

class AccountMovePutResponse(Datamodel):
    _name = "account.move.put.response"

    code = fields.Integer(required=True, allow_none=False)
    message = fields.String(required=False, allow_none=False)