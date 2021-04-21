#encoding: utf-8
from odoo import api, fields, models

class ProductBannerConfig(models.Model):
    # _inherit = ['res.partner']
    _name = "product.banner.config"
    _description = "Configuración de Banners"

    type = fields.Selection([('banner','Banner'),('footer','Pie'),('product','Producto'),('event','Event')])
    product_category_id = fields.Many2one("product.category",string="Associated Product Category")
    product_id = fields.Many2one("product.template",string="Associated Product")
    ir_attachment_id = fields.Many2one("ir.attachment", string="Attachment Resource",
                                       domain="[('type','=','binary'),('mimetype','=','image/png')]")
    banner_image = fields.Binary(string='Banner Image')
    link = fields.Char(string="Banner Link")
    button_link = fields.Char(string="Button Link")
    bg_color = fields.Char(string="Background Color")
    priority = fields.Integer(string="Priority")

    @api.onchange("ir_attachment_id")
    def _onchange_ir_attachment_id(self):
        print(self.ir_attachment_id.id)
        attachment = self.env["ir.attachment"].browse(self.ir_attachment_id.id)
        if attachment:
            self.banner_image = attachment.datas
        else:
            self.banner_image = False
