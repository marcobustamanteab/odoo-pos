odoo.define('ccu_pos.PaymentLinesValidator', function (require) {
    "use strict";

    const { useListener } = require('web.custom_hooks');
    const PaymentScreenPaymentLines = require('point_of_sale.PaymentScreenPaymentLines');
    const Registries = require('point_of_sale.Registries');

    const PaymentLinesValidator = PaymentScreenPaymentLines =>
        class extends PaymentScreenPaymentLines {
            constructor() {
                super(...arguments);
                useListener('del-transbank-line', this.delPaymentLine);
                useListener('edit-transbank-line', this.editPaymentLine);
            }
            async editPaymentLine(event) {
                var self = this;
                const { confirmed, payload } = await this.showPopup('NumberPopup', {
                   title: this.env._t('Ingrese ID Transbank'),
                   body: this.env._t('This click is successfully done.'),
                });
                if (confirmed) {
                   console.log(payload, 'payload')
                    this.env.pos.attributes.selectedOrder.paymentlines.models[0].transaction_id = payload;
                }
                this.render();
            }
            async delPaymentLine(event) {
                this.env.pos.attributes.selectedOrder.paymentlines.models[0].transaction_id = 0;
                this.render();
            }
            getPaymentLines(){
                return this.env.pos.attributes.selectedOrder.paymentlines.models[0];
            }
            get transactionId(){
                return this.getPaymentLines().transaction_id;
            }
            get transactionNameVal(){
                return this.getPaymentLines().name;
            }
        }

    Registries.Component.extend(PaymentScreenPaymentLines, PaymentLinesValidator);

    return PaymentLinesValidator;

});
