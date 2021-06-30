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
                const context = this.state.editModeProps.partner;
                // const context = this.props;
                if (context.is_company && !context.name || !context.vat
                    || !context.l10n_cl_activity_description || !context.l10n_cl_sii_taxpayer_type
                    || !context.address || !context.city || !context.country_id || !context.state_id){
                        return this.showPopup('ErrorPopup', {
                          title: ('Ingrese los datos requeridos'),
                        });
                } else if (!context.is_company && !context.name || !context.address
                    || !context.city || !context.country_id || !context.state_id){
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
