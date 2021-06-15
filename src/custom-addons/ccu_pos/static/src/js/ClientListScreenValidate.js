odoo.define('ccu_pos.ClientListScreenValidate', function (require) {
    "use strict";

    const { useListener } = require('web.custom_hooks');
    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Registries = require('point_of_sale.Registries');

    const ClientListScreenValidate = ClientListScreen =>
        class extends ClientListScreen {
            constructor() {
                super(...arguments);
                useListener('click-refresh', this.clickRefresh);
                useListener('click-save-transbank', this.clickSaveTransbank);
                useListener('activate-pos-clear', this.activateEditClear);
            }
            async clickRefresh(){
                await this.env.pos.load_new_partners();
                // create_from_ui
            }
            get refreshButton(){
                return { command: 'refresh', text: 'Refrescar Cliente' };
            }
            async clickSaveTransbank(){
                const context = this.state.editModeProps;
                if (context.partner.is_company && !context.partner.name || !context.partner.vat
                    || !context.partner.l10n_cl_activity_description || !context.partner.l10n_cl_sii_taxpayer_type
                    || !context.partner.address || !context.partner.city || !context.partner.country || !context.partner.state){
                        return this.showPopup('ErrorPopup', {
                          title: ('Ingrese los datos requeridos'),
                        });
                } else if (!context.partner.is_company && !context.partner.name || !context.partner.address
                    || !context.partner.city || !context.partner.country || !context.partner.state){
                        return this.showPopup('ErrorPopup', {
                          title: ('Ingrese los datos requeridos'),
                        });
                } else {
                    this.env.bus.trigger('save-customer');
                }
            }
            activateEditClear(){
                console.log("aqui");
                this.state.editModeProps = {
                    partner: null,
                };
                this.env.bus.trigger('activate-edit-mode', { isNewClient: true });
            }
        }

    Registries.Component.extend(ClientListScreen, ClientListScreenValidate);

    return ClientListScreen;

});
