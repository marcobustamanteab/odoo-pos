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
            async validateOrderTransbank(event) {
                if(this.env.pos.config.cash_rounding) {
                    if(!this.env.pos.get_order().check_paymentlines_rounding()) {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Rounding error in payment lines'),
                            body: this.env._t("The amount of your payment lines must be rounded to validate the transaction."),
                        });
                        return;
                    }
                }
                if (await this._isOrderValid(isForceValidate)) {
                    // remove pending payments before finalizing the validation
                    for (let line of this.paymentLines) {
                        if (!line.is_done()) this.currentOrder.remove_paymentline(line);
                    }
                    await this._finalizeValidation();
                }
            }
        }

    Registries.Component.extend(PaymentScreen, PaymentScreenValidator);

    return PaymentScreenValidator;

});
