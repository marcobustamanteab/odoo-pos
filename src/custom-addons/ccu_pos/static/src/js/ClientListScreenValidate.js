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
                }


              // try {
              //       let partnerId = await this.rpc({
              //           model: 'res.partner',
              //           method: 'create_from_ui',
              //           args: [event.detail.processedChanges],
              //       });
              //       await this.env.pos.load_new_partners();
              //       this.state.selectedClient = this.env.pos.db.get_partner_by_id(partnerId);
              //       this.state.detailIsShown = false;
              //       this.render();
              //   } catch (error) {
              //       if (error.message.code < 0) {
              //           await this.showPopup('OfflineErrorPopup', {
              //               title: this.env._t('Offline'),
              //               body: this.env._t('Unable to save changes.'),
              //           });
              //       } else {
              //           throw error;
              //       }
              //   }





            }
        }

    Registries.Component.extend(ClientListScreen, ClientListScreenValidate);

    return ClientListScreen;

});
