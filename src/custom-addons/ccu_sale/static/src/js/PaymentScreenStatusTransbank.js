odoo.define('ccu_sale.PaymentScreenStatusTransbank', function (require) {
    "use strict";

    const PaymentScreenStatus = require('point_of_sale.PaymentScreenStatus');
    const Registries = require('point_of_sale.Registries');

    const PaymentScreenStatusTransbank = PaymentScreenStatus =>
        class extends PaymentScreenStatus {

            constructor() {
                super(...arguments);
            }
            getTransactionId(){
                return this.env.pos.format_currency_no_symbol(this.env.pos.attributes.selectedOrder.paymentlines.models[0].transaction_id);
            }
            getTransactionName(){
                return this.env.pos.attributes.selectedOrder.paymentlines.models[0].name;
            }
        }

    Registries.Component.extend(PaymentScreenStatus, PaymentScreenStatusTransbank);

    return PaymentScreenStatusTransbank;

});
