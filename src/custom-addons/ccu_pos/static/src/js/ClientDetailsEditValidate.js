odoo.define('ccu_pos.ClientDetailsEditValidate', function (require) {
    "use strict";

    const { useListener } = require('web.custom_hooks');
    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');
    const Registries = require('point_of_sale.Registries');

    const ClientDetailsEditValidate = ClientDetailsEdit =>
        class extends ClientDetailsEdit {
            constructor() {
                super(...arguments);
                // useListener('save-payment-line', this.validateOrderTransbank);
            }
            // getTransactionName(){
            //     return this.env.pos.attributes.selectedOrder.paymentlines.models[0].name;
            // }
            // validateOrderTransbank(event) {
            //     if(this.env.pos.attributes.selectedOrder.paymentlines.models[0].transaction_id > 99999){
            //         this.validateOrder(false);
            //     }
            //     this.render();
            // }
        }

    Registries.Component.extend(ClientDetailsEdit, ClientDetailsEditValidate);

    return ClientDetailsEditValidate;

});
