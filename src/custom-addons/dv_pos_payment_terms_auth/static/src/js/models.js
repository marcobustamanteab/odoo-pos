odoo.define('dv_pos_payment_terms_auth.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    models.load_fields('pos.payment.method', ['payment_term_ids', 'use_payment_terms', 'needs_authorization_code']);
    
    models.load_models([
        {
            model: 'account.payment.term',
            fields: ['name'],
            domain: function () { return [['active', '=', true]]; },
            loaded: function (self, terms) {
                self.payment_terms = {};
                _.map(terms, function (term) {
                    self.payment_terms[term.id] = {
                        id: term.id,
                        name: term.name,
                    }
                });
            }
        }
    ]);
    var exports = models.exports;
    // Overrides the PaymentMethod exports to send data to backend of the payment terms
    var _super_paymentline = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        initialize: function (attributes, options) {
            this.payment_terms = '';
            this.payment_authorization_code = '';
            _super_paymentline.initialize.apply(this, arguments);
        },

        init_from_JSON: function (json) {
            this.payment_terms = json.payment_terms;
            this.payment_authorization_code = json.payment_authorization_code;
            _super_paymentline.init_from_JSON.apply(this, arguments);
        },

        set_payment_terms: function (value) {
            this.payment_terms = value;
            this.trigger('change', this);
        },

        set_payment_authorization_code: function (value) {
            this.payment_authorization_code = value;
            this.trigger('change', this);
        },

        export_as_JSON: function () {
            var result = _super_paymentline.export_as_JSON.apply(this, arguments);
            result.payment_terms = this.payment_terms;
            result.payment_authorization_code = this.payment_authorization_code;
            return result;
        },
        export_for_printing: function(){
            var json = _super_paymentline.export_for_printing.apply(this,arguments);
            json.payment_authorization_code = this.payment_authorization_code
            return json;
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_paymentline: function (payment_method) {
            this.assert_editable();
            var self = this
            var newPaymentline = new models.Paymentline({}, { order: this, payment_method: payment_method, pos: this.pos });
            newPaymentline.set_amount(this.get_due());
            newPaymentline.set_payment_terms(payment_method.payment_terms);
            newPaymentline.set_payment_authorization_code(payment_method.payment_authorization_code);
            this.paymentlines.add(newPaymentline);
            this.select_paymentline(newPaymentline);
            return newPaymentline;
        },
        export_for_printing: function(){
            var json = _super_order.export_for_printing.apply(this,arguments);
            return json;
        },
    });
});
