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
                this.currentOrder.set_to_invoice(true);
            }
            getTransactionName(){
                return this.env.pos.attributes.selectedOrder.paymentlines.models[0].name;
            }
            async validateOrderTransbank(isForceValidate) {

                // Order quantities validation
                const order_lines = this.env.pos.get_order().get_orderlines()
                const products = order_lines.map(({ quantity, product }) => [quantity, product.product_tmpl_id])
                const validate_category_quantities = await this.rpc({
                    model: 'res.partner',
                    method: 'validate_category_quantities',
                    args: [this.currentOrder.get_client(), products],
                    kwargs: {},
                })

                if (validate_category_quantities) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Error en la validación de cantidades'),
                        body: this.env._t(validate_category_quantities),
                    });
                    return false;
                }

                if(this.env.pos.config.cash_rounding) {
                    if(!this.env.pos.get_order().check_paymentlines_rounding()) {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Rounding error in payment lines'),
                            body: this.env._t("The amount of your payment lines must be rounded to validate the transaction."),
                        });
                        return;
                    }
                }
                if (await this._isOrderValidTransbank(isForceValidate)) {
                    // remove pending payments before finalizing the validation
                    for (let line of this.paymentLines) {
                        if (!line.is_done()) {
                            this.currentOrder.remove_paymentline(line);
                        }
                    }
                    await this._finalizeValidation();
                }
            }
            async _isOrderValidTransbank(isForceValidate) {

                if (this.currentOrder.get_orderlines().length === 0) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Empty Order'),
                        body: this.env._t(
                            'There must be at least one product in your order before it can be validated'
                        ),
                    });
                    return false;
                }

                if (this.currentOrder.get_orderlines().length === 0) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Empty Order'),
                        body: this.env._t(
                            'There must be at least one product in your order before it can be validated'
                        ),
                    });
                    return false;
                }

                if (this.currentOrder.is_to_invoice() && !this.currentOrder.get_client()) {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Please select the Customer'),
                        body: this.env._t(
                            'You need to select the customer before you can invoice an order.'
                        ),
                    });
                    if (confirmed) {
                        this.selectClient();
                    }
                    return false;
                }

                if (!this.currentOrder.is_paid() || this.invoicing) {
                    return false;
                }

                if (this.currentOrder.has_not_valid_rounding()) {
                    var line = this.currentOrder.has_not_valid_rounding();
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Incorrect rounding'),
                        body: this.env._t(
                            'You have to round your payments lines.' + line.amount + ' is not rounded.'
                        ),
                    });
                    return false;
                }

                // The exact amount must be paid if there is no cash payment method defined.
                if (
                    Math.abs(
                        this.currentOrder.get_total_with_tax() - this.currentOrder.get_total_paid()  + this.currentOrder.get_rounding_applied()
                    ) > 0.00001
                ) {
                    var cash = false;
                    for (var i = 0; i < this.env.pos.payment_methods.length; i++) {
                        cash = cash || this.env.pos.payment_methods[i].is_cash_count;
                    }
                    if (!cash) {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Cannot return change without a cash payment method'),
                            body: this.env._t(
                                'There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'
                            ),
                        });
                        return false;
                    }
                }

                // if the change is too large, it's probably an input error, make the user confirm.
                if (
                    !isForceValidate &&
                    this.currentOrder.get_total_with_tax() > 0 &&
                    this.currentOrder.get_total_with_tax() * 1000 < this.currentOrder.get_total_paid()
                ) {
                    this.showPopup('ConfirmPopup', {
                        title: this.env._t('Please Confirm Large Amount'),
                        body:
                            this.env._t('Are you sure that the customer wants to  pay') +
                            ' ' +
                            this.env.pos.format_currency(this.currentOrder.get_total_paid()) +
                            ' ' +
                            this.env._t('for an order of') +
                            ' ' +
                            this.env.pos.format_currency(this.currentOrder.get_total_with_tax()) +
                            ' ' +
                            this.env._t('? Clicking "Confirm" will validate the payment.'),
                    }).then(({ confirmed }) => {
                        if (confirmed) this.validateOrder(true);
                    });
                    return false;
                }

                return true;
            }
        }

    Registries.Component.extend(PaymentScreen, PaymentScreenValidator);

    return PaymentScreen;

});
