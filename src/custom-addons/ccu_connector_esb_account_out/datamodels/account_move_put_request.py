from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel

class PickingPutRequest(Datamodel):
    _name = "picking.put.request"

    sync_uuid = fields.String(required=True, allow_none=False)
    reference = fields.String(required=False, allow_none=False)