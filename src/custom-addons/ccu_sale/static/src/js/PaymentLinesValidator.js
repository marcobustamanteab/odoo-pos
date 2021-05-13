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
                NumberBufferTrx.use({
                    // The numberBuffer listens to this event to update its state.
                    // Basically means 'update the buffer when this event is triggered'
                    nonKeyboardInputEvent: 'input-from-numpad',
                    // When the buffer is updated, trigger this event.
                    // Note that the component listens to it.
                    triggerAtInput: 'update-selected-paymentline',
                });
            }

            savePaymentLine(event) {
                line.transbank_saved = true
                line.transaction_id = NumberBufferTrx.getText();

                NumberBuffer.reset();
                this.render();
            }

            editPaymentLine(event) {
                line.transbank_saved = false
                line.transaction_id = NumberBufferTrx.getText();

                NumberBuffer.reset();
                this.render();
            }

            updateTransbankPaymentline() {
                line.transaction_id = NumberBufferTrx.getText();
                this.render();
            }
        }

    Registries.Component.extend(PaymentScreenPaymentLines, PaymentTransbankLinesValidator);

    return PaymentTransbankLinesValidator;

});
