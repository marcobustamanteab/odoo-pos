odoo.define('ccu_sale.OrderReceiptTransbank', function (require) {
    "use strict";

    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');

    const OrderReceiptTransbank = OrderReceipt =>
        class extends OrderReceipt {
            constructor() {
                super(...arguments);

            }
            getTransactionId(){
                return this.env.pos.attributes.selectedOrder.paymentlines.models[0].transaction_id;
            }
            getTransactionName(){
                return this.env.pos.attributes.selectedOrder.paymentlines.models[0].name;
            }
        }

    Registries.Component.extend(OrderReceipt, OrderReceiptTransbank);

    return OrderReceiptTransbank;

});
