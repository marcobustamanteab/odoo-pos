from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel

class MovePutResponse(Datamodel):
    _name = "move.put.response"

    code = fields.Integer(required=True, allow_none=False)
    message = fields.String(required=False, allow_none=False)