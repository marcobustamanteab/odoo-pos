odoo.define('ccu_sale.PaymentTransbankLinesValidator', function (require) {
    "use strict";

    const { xml } = owl.tags;
    const { useListener } = require('web.custom_hooks');
    const PaymentScreenPaymentLines = require('point_of_sale.PaymentScreenPaymentLines');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const NumberBufferTrx = require('point_of_sale.NumberBuffer');
    const Registries = require('point_of_sale.Registries');

    const PaymentTransbankLinesValidator = PaymentScreenPaymentLines =>
        class extends PaymentScreenPaymentLines {
            constructor() {
                super(...arguments);
                useListener('save-payment-line', this.savePaymentLine);
                useListener('edit-payment-line', this.editPaymentLine);
                useListener('update-selected-paymentline', this.updateTransbankPaymentline);
                // this.props.paymentLines[0].transaction_id = 1234;
                NumberBufferTrx.use({
                    // The numberBuffer listens to this event to update its state.
                    // Basically means 'update the buffer when this event is triggered'
                    nonKeyboardInputEvent: 'input-from-numpad',
                    // When the buffer is updated, trigger this event.
                    // Note that the component listens to it.
                    triggerAtInput: 'update-selected-paymentline',
                });
            }
            getTransactionId(){
                return this.props.paymentLines[0].transaction_id;
            }
            getTransactionName(){
                return this.getPaymentLines().name;
            }
            savePaymentLine(event) {
                //this.props.paymentlines.transbanksaved = false;
                this.env.pos.attributes.selectedOrder.paymentlines.models[0].transaction_id = this.env.pos.attributes.selectedOrder.paymentlines.models[0].amount;
                // this.NumberBufferTrx = PaymentScreen.buffer;
                // this.props.paymentlines.transaction_id = NumberBufferTrx.getText();

                // NumberBuffer.reset();
                this.render();
            }
            editPaymentLine(event) {
                this.env.pos.attributes.selectedOrder.paymentlines.models[0].transaction_id = 0;
                this.render();
            }
            getPaymentLines(){
                return this.props.paymentLines[0];
            }
            updateTransbankPaymentline() {
                line.transaction_id = NumberBufferTrx.getText();
                this.render();
            }
        }

    Registries.Component.extend(PaymentScreenPaymentLines, PaymentTransbankLinesValidator);

    return PaymentTransbankLinesValidator;

});
