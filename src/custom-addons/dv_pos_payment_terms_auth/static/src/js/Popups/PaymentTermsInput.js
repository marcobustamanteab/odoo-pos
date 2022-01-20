odoo.define('dv_pos_payment_terms_auth.PaymentTermsInput', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class PaymentTermsInput extends PosComponent {
        onKeyup(event) {
            if (event.key === "Enter" && event.target.value.trim() !== '') {
                this.trigger('create-new-item');
            }
        }
    }
    PaymentTermsInput.template = 'PaymentTermsInput';

    Registries.Component.add(PaymentTermsInput);

    return PaymentTermsInput;
});
