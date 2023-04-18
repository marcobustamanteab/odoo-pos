# -*- coding: utf-8 -*-
from odoo.addons.base_rest.controllers.api_docs import ApiDocsController
from odoo.http import request, route


class CCUApiDocsController(ApiDocsController):

    @route(["/api-docs", "/api-docs/index.html"], methods=["GET"], type="http", auth="user", csrf=False)
    def index(self, **params):
        self._get_api_urls()
        primary_name = params.get("urls.primaryName")
        values = {"api_urls": self._get_api_urls(), "primary_name": primary_name}
        return request.render("base_rest.openapi", values)

    @route("/api-docs/<path:collection>/<string:service_name>.json", auth="user", csrf=False)
    def api(self, collection, service_name):
        with self.service_component(collection, service_name) as service:
            return self.make_json_response(service.to_openapi())
