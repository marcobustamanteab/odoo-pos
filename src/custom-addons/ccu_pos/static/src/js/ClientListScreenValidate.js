odoo.define('ccu_pos.ClientListScreenValidate', function (require) {
    "use strict";

    const { _t } = require('web.core');
    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');

    const ClientListScreenValidate = ClientListScreen =>
        class extends ClientListScreen {
            constructor() {
                super(...arguments);
                useListener('click-refresh', this.clickRefresh);
                useListener('click-save-transbank', () => this.env.bus.trigger('prepare-customer-pos'));
                useListener('save-customer-pos', this.saveCustomer);
                useListener('activate-pos-clear', this.activateEditClear);
                this.controlClienterPos = {
                    'saved_customer' : false,
                    'last_save_customer' : null
                };
            }
            clickRefresh(){
                var domain = [];
                var fields = [];
                let partners = null;
                this.rpc({
                    model: 'res.partner',
                    method: 'search_read',
                    args: [domain, fields],
                    kwargs: {},
                }).then(function (partner) {
                    if (partner.length > 0) {
                        partners = partner;
                    } else {
                        this.showPopup('ErrorPopup', { body: 'No previous orders found' });
                    }
                });
                this.env.pos.partners = partners;
                this.render();
            }
            get refreshButton(){
                return { command: 'refresh', text: 'Refrescar Cliente' };
            }
            verifyCustomerSelected(){
                let verified = false;
                let nameVerified = [];
                let context = this.state.selectedClient;
                const rgEmail = /[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,4}/g;
                const rgTel = /[0-9]{9}/g;
                const rgCel = /[0-9]{9}/g;
                const rgRut = /^[0-9]+-[0-9kK]{1}$/g;

                if(context != null){
                    let valueCel = rgCel.test(context.mobile);
                    let valueRut = rgRut.test(context.vat);
                    context.mobile ? valueCel ? nameVerified[nameVerified.length] = 'Celular' : nameVerified[nameVerified.length] = 'Celular-Formato' : nameVerified[nameVerified.length] = 'Celular-Formato';
                    context.street ? nameVerified[nameVerified.length] = 'Calle' : nameVerified[nameVerified.length] = 'Calle-Formato';
                    context.city_id ? nameVerified[nameVerified.length] = 'Comuna' : nameVerified[nameVerified.length] = 'Comuna-Formato';
                    context.vat ? valueRut ? nameVerified[nameVerified.length] = 'RUT' : nameVerified[nameVerified.length] = 'RUT-Formato' : nameVerified[nameVerified.length] = 'RUT-Formato';
                    context.l10n_cl_activity_description ? nameVerified[nameVerified.length] = 'Giro': nameVerified[nameVerified.length] = 'Giro-Formato';
                    }else{
                        nameVerified[nameVerified.length] = 'Celular-Formato';
                        nameVerified[nameVerified.length] = 'Calle-Formato';
                        nameVerified[nameVerified.length] = 'Comuna-Formato';
                        nameVerified[nameVerified.length] = 'RUT-Formato';
                        nameVerified[nameVerified.length] = 'Giro-Formato';
                }
                nameVerified.length === 0 ? verified = true : verified = false;
                return { 'verified' : verified, 'nameVerified' : nameVerified};
            }
            verifyChangeCustomer(data){
                let verified = false;
                let nameVerified = [];
                const rgEmail = /[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,4}/g;
                const rgTel = /[0-9]{9}/g;
                const rgCel = /[0-9]{9}/g;
                const rgRut = /^[0-9]+-[0-9kK]{1}$/g;
                let valueTel = rgTel.test(data.phone);
                let valueCel = rgCel.test(data.mobile);
                let valueRut = rgRut.test(data.vat);
                console.log('val cel -> ' + rgTel.test(data.mobile));
                console.log('val rut -> ' + rgRut.test(data.vat));
                console.log('ver cel -> ' + data.mobile);
                console.log('ver rut -> ' + data.vat);
                if(data != null){
                    data.mobile === null || data.mobile === '' || data.mobile === undefined ? console.log('verificacion changed 2') : valueCel ? nameVerified[nameVerified.length] = 'Celular' : nameVerified[nameVerified.length] = 'Celular-Formato';
                    data.street === null || data.street === '' || data.street === undefined ? console.log('verificacion changed 4') : nameVerified[nameVerified.length] = 'Calle';
                    data.city_id === null || data.city_id === '' || data.city_id === undefined || data.city_id === false ? console.log('verificacion changed 7') : nameVerified[nameVerified.length] = 'Comuna';
                    data.vat === null || data.vat === '' || data.vat === undefined ? console.log('verificacion changed 8') : valueRut ? nameVerified[nameVerified.length] = 'RUT' : nameVerified[nameVerified.length] = 'RUT-1';
                    data.l10n_cl_activity_description === null || data.l10n_cl_activity_description === '' || data.l10n_cl_activity_description === undefined ? console.log('verificacion changed 11') : nameVerified[nameVerified.length] = 'Giro';
                    }
                nameVerified.length === 0 ? verified = true : verified = false;
                return { 'verified' : verified, 'nameVerified' : nameVerified};
            }

            async saveCustomer(event){
                let data = event.detail.processedChanges;
                if(data != null) {
                  if(data.dob == null){
                    data.dob = '2000-01-01'
                  }
                  if(data.vat != null){
                    data.vat = data.vat.toUpperCase()
                  }
                  if(data.l10n_cl_dte_email == null){
                    data.l10n_cl_dte_email = 'facturacionmipyme@sii.cl'
                  }


                    let verifiedSavedCustomer = this.verifyCustomerSelected();
                    let verifiedChangeCustomer = this.verifyChangeCustomer(data);
                    console.log('verifiedSavedCustomer : ' + verifiedSavedCustomer.verified
                    + ' verifiedChangeCustomer : ' + verifiedChangeCustomer.verified);
                    var unifiedResponse = this.unifiedResponse(verifiedChangeCustomer.nameVerified, verifiedSavedCustomer.nameVerified);
                    if (unifiedResponse.length === 0) {
                        try {
                            let partnerId = await this.rpc({
                                model: 'res.partner',
                                method: 'create_from_ui',
                                args: [event.detail.processedChanges],
                            });
                            await this.rpc({
                                    model: 'res.partner',
                                    method: 'onchange_city_id',
                                    args: [partnerId],
                                });
                            await this.env.pos.load_new_partners();
                            this.state.selectedClient = this.env.pos.db.get_partner_by_id(partnerId);
                            this.state.detailIsShown = false;
                            this.render();
                        } catch (error) {
                            if (error.message.code < 0) {
                                await this.showPopup('OfflineErrorPopup', {
                                    title: this.env._t('Offline'),
                                    body: this.env._t('Unable to save changes.'),
                                });
                            } else {
                                throw error;
                            }
                        }
                    }else{
                        this.showPopup('ErrorPopup', { body: 'Debe ingresar los campos obligatorios en ' + (unifiedResponse.length > 1 ? 'los campos ' : 'el campo ') + unifiedResponse});
                    }
                } else {
                    this.showPopup('ErrorPopup', { body: 'No se detectan cambios en el Cliente.' });
                }
            }
            unifiedResponse(change,custom) {
                var unifiedResponse = [];
                custom.forEach(function (elem, index) {
                    var compare = ''; /* F = problema formato ; SD = sin data ; */
                    var element = elem;
                    var b = element.split('-');
                    if( b.length === 1){
                        change.forEach(function (chan, index) {
                            var a = chan.split('-');
                            if (a[0] === element) {
                                if( a.length > 1 ){
                                    compare = 'PE';
                                    console.log('presente con error en -> ' + chan);
                                }else{
                                    compare = 'PS';
                                    console.log('presente sin error en -> ' + chan);
                                }
                            }
                        });
                        if(compare === 'PS') {
                            compare = 'SD';
                        }else{
                            compare = 'SD';
                        }
                    }else{
                        console.log('saved con error en -> ' + element);

                        change.forEach(function (chan, index) {
                            var a = chan.split('-');
                            var loga = a[0];
                            var logb = b[0];
                            console.log('loga -> ' + loga);
                            console.log('logb -> ' + logb);
                            if (a[0] === b[0]) {
                                if( a.length === 1 ){
                                    compare = 'SD';
                                    console.log('sin dato');
                                }
                            }
                        });
                    }
                    // compare === 'SD' ? '' : unifiedResponse[unifiedResponse.length] = element;taxpayer
                    b === 'Formato' ? '' : compare === 'SD' ? '' : unifiedResponse[unifiedResponse.length] = ' ' + b[0];
                    console.log('elem -> ' + unifiedResponse[unifiedResponse.length - 1]);
                });
                return unifiedResponse;
            }

            activateEditClear(){
                console.log("aqui");
                this.state.editModeProps = {
                    partner: null,
                };
                this.env.bus.trigger('activate-edit-mode', { isNewClient: true });
            }
        }
// }
    Registries.Component.extend(ClientListScreen, ClientListScreenValidate);

    return ClientListScreen;

});
