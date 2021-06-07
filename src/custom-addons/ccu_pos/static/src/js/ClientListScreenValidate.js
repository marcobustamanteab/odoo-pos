odoo.define('ccu_pos.ClientListScreenValidate', function (require) {
    "use strict";

    const { useListener } = require('web.custom_hooks');
    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Registries = require('point_of_sale.Registries');

    const ClientListScreenValidate = ClientListScreen =>
        class extends ClientListScreen {
            constructor() {
                super(...arguments);
            }
            clickRefresh(){
                return true;
            }
            get refreshButton(){
                return { command: 'refresh', text: 'Refrescar Cliente' };
            }
        }

    Registries.Component.extend(ClientListScreen, ClientListScreenValidate);

    return ClientListScreen;

});
