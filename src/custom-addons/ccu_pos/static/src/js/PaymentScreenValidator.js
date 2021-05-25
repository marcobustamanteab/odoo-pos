odoo.define('ccu_pos.PaymentScreenValidator', function (require) {
    "use strict";

    const { useListener } = require('web.custom_hooks');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const PaymentScreenValidator = PaymentScreen =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
                useListener('save-payment-line', this.validateOrderTransbank);
            }
            getTransactionName(){
                return this.env.pos.attributes.selectedOrder.paymentlines.models[0].name;
            }
            validateOrderTransbank(event) {
                if(this.env.pos.attributes.selectedOrder.paymentlines.models[0].transaction_id > 99999){
                    this.validateOrder(false);
                }
                this.render();
            }
        }

    Registries.Component.extend(PaymentScreen, PaymentScreenValidator);

    return PaymentScreenValidator;

});
