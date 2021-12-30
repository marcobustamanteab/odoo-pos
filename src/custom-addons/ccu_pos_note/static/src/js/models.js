odoo.define('tis_pos_order_notes.order', function (require) {
"use strict";

    var models = require('point_of_sale.models');

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr, options) {
            _super_orderline.initialize.call(this,attr,options);
            this.note = this.note || "";
        },
        set_note: function(note){
            this.note = note;
            this.trigger('change',this);
        },
        get_note: function(note){
            return this.note;
        },
        can_be_merged_with: function(orderline) {
            if (orderline.get_note() !== this.get_note()) {
                return false;
            } else {
                return _super_orderline.can_be_merged_with.apply(this,arguments);
            }
        },
        clone: function(){
            var orderline = _super_orderline.clone.call(this);
            orderline.note = this.note;
            return orderline;
        },
        export_for_printing: function () {
            var receipt_line = _super_orderline.export_for_printing.call(this);
            console.log('receipt_line',receipt_line)
            receipt_line['note'] = this.note || '';
            return receipt_line;
        },
        export_as_JSON: function(){
            var json = _super_orderline.export_as_JSON.call(this);
            json.note = this.note;
            return json;
        },
        init_from_JSON: function(json){
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.note = json.note;
        },
    });

    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            _super_Order.initialize.apply(this, arguments);
            var self = this;
            if (!this.note) {
                this.note = '';
            }
        },
        init_from_JSON: function (json) {
            var res = _super_Order.init_from_JSON.apply(this, arguments);
            if (json.note) {
                this.note = json.note
            }
            return res;
        },
        export_as_JSON: function () {
            var json = _super_Order.export_as_JSON.apply(this, arguments);
            if (this.note) {
                json.note = this.note;
            }
            return json;
        },
        export_for_printing: function () {
            var receipt = _super_Order.export_for_printing.call(this);
            receipt['note'] = this.note;
            receipt['signature'] = this.signature;

            return receipt;
        },
        set_note: function (note) {
            this.note = note;
            this.trigger('change', this);
        },
        get_note: function (note) {
            return this.note;
        },
    });

});
