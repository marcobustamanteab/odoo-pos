odoo.define('dv_pos_payment_terms_auth.PaymentMethodButton', function (require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const PaymentMethodButton = require('point_of_sale.PaymentMethodButton');

    const PaymentTermsPaymentMethodButton = PaymentMethodButton =>
        class extends PaymentMethodButton {
            _get_payment_terms_data_from_ids(terms_ids) {
                // mapear con los account.payment.term
                var payment_terms_data = _.map(terms_ids, (id) => this.env.pos.payment_terms[id])
                return payment_terms_data
            }

            async click_payment_method() {
                var self = this;
                this.props.paymentMethod.text = ''
                this.props.paymentMethod.auth_code = ''
                if (!this.props.paymentMethod.use_payment_terms && !this.props.paymentMethod.needs_authorization_code) {
                    this.trigger('new-payment-line', this.props.paymentMethod)
                } else {
                    var payment_terms_data = this._get_payment_terms_data_from_ids(this.props.paymentMethod.payment_term_ids)
                    const { confirmed, payload } = await self.showPopup('PaymentTermsPopup', {
                        title: this.env._t('Código de Autorización'),
                        payment_terms: payment_terms_data,
                        isSingleItem: true,
                        array: [this.props.paymentMethod],
                    });

                    if (confirmed && payload.newArray[0].auth_code) {
                        // Send the input value to payment_terms
                        this.props.paymentMethod.payment_terms = payload.newArray[0].text
                        this.props.paymentMethod.payment_authorization_code = payload.newArray[0].auth_code
                        this.trigger('new-payment-line', this.props.paymentMethod)
                    } else {
                      this.showPopup('ErrorPopup', {
                            title: 'Transbank',
                            body: 'Debe ingresar un ID de Transbank para continuar la transacción',
                        });
                        return false;

                    }
                }
            }
        }
    Registries.Component.extend(PaymentMethodButton, PaymentTermsPaymentMethodButton);

    return PaymentMethodButton;
});
