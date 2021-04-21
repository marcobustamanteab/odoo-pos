# encoding: utf-8
from odoo import api, fields, models
from odoo.http import content_disposition, Controller, request, route, Response
import json
import datetime
import base64


class WebSiteContentApi(Controller):

    @route('/Delivery/Dates', methods=['GET'], auth='public', csrf=False, cors="*")
    def product_banner_api(self):
        resData = {}
        resData["dates"] = []

        req = request.httprequest

        sale_date = req.values.get("date", "-1")
        district_code = req.values.get("district-code", "-1")

        if sale_date == "-1":
            resData["ErrorCode"] = "500"
            resData["ErrorDescription"] = "Invalid Sale Date"
            return json.dumps(resData)
        if district_code == "-1":
            resData["ErrorCode"] = "500"
            resData["ErrorDescription"] = "Invalid District Code"
            return json.dumps(resData)

        district = request.env["res.city.district"].search(
            [
                ("code", "=", district_code)
            ]
        )
        if len(district) == 0:
            resData["ErrorCode"] = "500"
            resData["ErrorDescription"] = "District Code not Found"
            return json.dumps(resData)
        initial_date = datetime.date(
            year=int(sale_date.split("-")[0]),
            month=int(sale_date.split("-")[1]),
            day=int(sale_date.split("-")[2]))
        limit_date = initial_date + datetime.timedelta(days=30)
        cl_id = request.env.ref('base.cl').id
        holidays = request.env["res.holiday"].search(
            [
                ('country_id','=',cl_id),
                ('date',">=",initial_date),
                ('date', "<=", limit_date)
            ]
        )
        holidays = [x.date for x in holidays]

        proc_date = initial_date + datetime.timedelta(days=district.lead_time or 0)
        while proc_date <= limit_date:
            if (proc_date.weekday() in [x.day_id for x in district.weekday_ids]) and (not proc_date in holidays):
                resData["dates"].append(str(proc_date))
            proc_date += datetime.timedelta(days=1)
        return json.dumps(resData)
