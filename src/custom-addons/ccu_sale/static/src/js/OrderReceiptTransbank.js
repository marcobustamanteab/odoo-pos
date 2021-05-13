odoo.define('ccu_sale.OrderReceiptTransbank', function (require) {
    "use strict";

    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');

    const OrderReceiptTransbank = OrderReceipt =>
        class extends OrderReceipt {
            constructor() {
                super(...arguments);

            }
        }

    Registries.Component.extend(OrderReceipt, OrderReceiptTransbank);

    return OrderReceiptTransbank;

});
