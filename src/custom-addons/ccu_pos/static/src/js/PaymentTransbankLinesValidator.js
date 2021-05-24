odoo.define('ccu_sale.PaymentTransbankLinesValidator', function (require) {
    "use strict";

    const { useListener } = require('web.custom_hooks');
    const PaymentScreenPaymentLines = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const PaymentTransbankLinesValidator = PaymentScreenPaymentLines =>
        class extends PaymentScreenPaymentLines {
            constructor() {
                super(...arguments);
                useListener('save-payment-line', this.savePaymentLine);
                useListener('edit-payment-line', this.editPaymentLine);
            }
            getTransactionId(){
                return this.getPaymentLines().transaction_id;
            }
            getTransactionName(){
                return this.getPaymentLines().name;
            }
            savePaymentLine(event) {
                if(this.env.pos.attributes.selectedOrder.paymentlines.models[0].transaction_id > 99999) {
                    this.env.pos.attributes.selectedOrder.paymentlines.models[0].transaction_id = this.env.pos.attributes.selectedOrder.paymentlines.models[0].amount;
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
        }

    Registries.Component.extend(PaymentScreenPaymentLines, PaymentTransbankLinesValidator);

    return PaymentTransbankLinesValidator;

});
