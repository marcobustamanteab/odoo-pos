odoo.define('ccu_pos.PaymentLinesValidator', function (require) {
    "use strict";

    const { useListener } = require('web.custom_hooks');
    const PaymentScreenPaymentLines = require('point_of_sale.PaymentScreenPaymentLines');
    const Registries = require('point_of_sale.Registries');

    const PaymentLinesValidator = PaymentScreenPaymentLines =>
        class extends PaymentScreenPaymentLines {
            constructor() {
                super(...arguments);
                useListener('save-payment-line', this.savePaymentLine);
                useListener('edit-payment-line', this.editPaymentLine);
            }
            savePaymentLine(event) {
                if(this.env.pos.attributes.selectedOrder.paymentlines.models[0].amount > 99999) {
                    this.env.pos.attributes.selectedOrder.paymentlines.models[0].transaction_id = this.env.pos.attributes.selectedOrder.paymentlines.models[0].amount;
                    this.env.pos.attributes.selectedOrder.paymentlines.models[0].amount = this.env.pos.attributes.selectedOrder.paymentlines.models[0].totalDueText;
                }else{
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Transbank Id Erroneo'),
                        body: this.env._t(
                            'Ingrese el numero correspondiente al voucher de Transbank.'
                        ),
                    });
                }
                this.render();
            }
            editPaymentLine(event) {
                this.env.pos.attributes.selectedOrder.paymentlines.models[0].transaction_id = 0;
                this.render();
            }
            getPaymentLines(){
                return this.env.pos.attributes.selectedOrder.paymentlines.models[0];
            }
            getTransactionId(){
                return this.getPaymentLines().transaction_id;
            }
            getTransactionNameVal(){
                return this.getPaymentLines().name;
            }
        }

    Registries.Component.extend(PaymentScreenPaymentLines, PaymentLinesValidator);

    return PaymentLinesValidator;

});
