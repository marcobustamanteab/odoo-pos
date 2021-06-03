odoo.define('ccu_pos.ClientLineValidate', function (require) {
    "use strict";

    const { useListener } = require('web.custom_hooks');
    const ClientLine = require('point_of_sale.ClientLine');
    const Registries = require('point_of_sale.Registries');

    const ClientLineValidate = ClientLine =>
        class extends ClientLine {
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

    Registries.Component.extend(ClientLine, ClientLineValidate);

    return ClientLineValidate;

});
