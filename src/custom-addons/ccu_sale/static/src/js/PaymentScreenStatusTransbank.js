odoo.define('ccu_sale.PaymentScreenStatusTransbank', function (require) {
    "use strict";

    const PaymentScreenStatus = require('point_of_sale.PaymentScreenStatus');
    const Registries = require('point_of_sale.Registries');

    const PaymentScreenStatusTransbank = PaymentScreenStatus =>
        class extends PaymentScreenStatus {

            constructor() {
                super(...arguments);
            }
        }

    Registries.Component.extend(PaymentScreenStatus, PaymentScreenStatusTransbank);

    return PaymentScreenStatusTransbank;

});
