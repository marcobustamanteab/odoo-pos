odoo.define('ccu_pos.ClientLineValidate', function (require) {
    "use strict";

    const { useListener } = require('web.custom_hooks');
    const ClientLine = require('point_of_sale.ClientLine');
    const Registries = require('point_of_sale.Registries');

    const ClientLineValidate = ClientLine =>
        class extends ClientLine {
            constructor() {
                super(...arguments);
            }
        }

    Registries.Component.extend(ClientLine, ClientLineValidate);

    return ClientLineValidate;

});
