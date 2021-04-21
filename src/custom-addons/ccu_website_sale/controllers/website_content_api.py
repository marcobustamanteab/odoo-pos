# encoding: utf-8
from odoo import api, fields, models
from odoo.http import content_disposition, Controller, request, route, Response
import json
import datetime
import base64


class WebSiteContentApi(Controller):

    # @route('/ContentApi/Products', methods=['GET'], auth='public', csrf=False, cors="*")  #for test
    @route('/ContentApi/Products', methods=['GET'], auth='user')
    def product_banner_api(self):
        resData = []

        req = request.httprequest
        search_word = req.headers.get(
            "SEARCH").strip()

        portal_user = request.env["res.users"].browse(request.env.uid)
        pricelist_id = -1
        if portal_user and portal_user.partner_id:
            pricelist_id = portal_user.partner_id.property_product_pricelist.id
        # pricelist_id = 1 #for test

        brand_list = request.env["product.brand"].search(
            [
                ('name', 'ilike', search_word)
            ]
        )

        for brand in brand_list:
            brand_info = {}
            brand_info["type"] = "brand"
            brand_info["name"] = brand.name
            brand_info["url"] = brand.url
            resData.append(brand_info)

        prod_list = request.env["product.pricelist.item"].search(
            [
                ('pricelist_id.id', '=', pricelist_id),
                ('applied_on', '=', '1_product')
            ]
        )

        for item in prod_list:
            flist = ["name","description","properties","categories","brand","tags"]
            product = item.product_tmpl_id
            prod_info = {}
            prod_info["type"] = "product"
            prod_info["id"] = product.id
            prod_info["code"] = product.default_code or ""
            prod_info["name"] = product.name
            prod_info["description"] = product.description_sale or ""
            prod_info["properties"] = ",".join([x.name for x in product.property_ids])
            prod_info["categories"] = ",".join([x.name for x in product.public_categ_ids])
            prod_info["brand"] = product.brand_id.name or ""
            prod_info["show_discount"] = item.show_discount
            prod_info["tags"] = ",".join([x.name for x in product.search_tag_ids])
            check_search = False
            for fname in flist:
                if search_word.lower() in prod_info[fname].lower():
                    check_search = True
                    break
            if check_search:
                resData.append(prod_info)
        return json.dumps(resData)
