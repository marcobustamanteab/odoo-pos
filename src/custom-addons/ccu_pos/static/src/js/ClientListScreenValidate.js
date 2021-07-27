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
                // this.verifySavedCustomer();
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
                // this.env.pos.partners = transp;
                this.render();
                // create_from_ui
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
                const rgRut = /^[0-9]+-[0-9kK]{1}$/g;

                if(context != null){
                    let valueEmail = rgEmail.test(context.l10n_cl_dte_email);
                    let valueTel = rgTel.test(context.phone);
                    let valueCel = rgTel.test(context.mobile);
                    let valueRut = rgRut.test(context.vat);
                    // context.phone === null || context.phone === '' || context.phone === false? console.log('verificacion saved 1 ') : valueTel ? nameVerified[nameVerified.length] = 'Telefono' : nameVerified[nameVerified.length] = 'Telefono-1';
                    // context.mobile === null || context.mobile === '' || context.mobile === false ? console.log('verificacion saved 2 ') : valueCel ? nameVerified[nameVerified.length] = 'Celular' : nameVerified[nameVerified.length] = 'Celular-1';
                    // context.l10n_cl_dte_email === null || context.l10n_cl_dte_email === '' || context.l10n_cl_dte_email ? console.log('verificacion saved 3 ') : valueEmail ? nameVerified[nameVerified.length] = 'Email_DTE' : nameVerified[nameVerified.length] = 'Email_DTE-1';
                    // context.street === null || context.street === '' || context.street ? console.log('verificacion saved 4 ') : nameVerified[nameVerified.length] = 'Calle'
                    // context.city === null || context.city === '' || context.city ? console.log('verificacion saved 5 ') : nameVerified[nameVerified.length] = 'Ciudad';
                    // context.country_id === null || context.country_id === '' || context.country_id ? console.log('verificacion saved 6 ') : nameVerified[nameVerified.length] = 'Pais';
                    // context.state_id === null || context.state_id === '' || context.state_id ? console.log('verificacion saved 7 ') : nameVerified[nameVerified.length] = 'Comuna';
                    // context.vat === null || context.vat === '' || context.vat ? console.log('verificacion saved 8 ') : valueRut ? nameVerified[nameVerified.length] = 'RUT' : nameVerified[nameVerified.length] = 'RUT-1';
                    // context.dob === null || context.dob === '' || context.dob ? console.log('verificacion saved 9 ') : nameVerified[nameVerified.length] = 'Fecha de Nacimiento';
                    // context.l10n_cl_sii_taxpayer_type === null || context.l10n_cl_sii_taxpayer_type === '' || context.l10n_cl_sii_taxpayer_type ? console.log('verificacion saved 10 ') : nameVerified[nameVerified.length] = 'Tipo Contribuyente';
                    // context.l10n_cl_activity_description === null || context.l10n_cl_activity_description === '' || context.l10n_cl_activity_description ? console.log('verificacion saved 11 ') : nameVerified[nameVerified.length] = 'Giro';

                    context.phone ? valueTel ? nameVerified[nameVerified.length] = 'Telefono' : nameVerified[nameVerified.length] = 'Telefono-Formato' : nameVerified[nameVerified.length] = 'Telefono-Formato';
                    context.mobile ? valueCel ? nameVerified[nameVerified.length] = 'Celular' : nameVerified[nameVerified.length] = 'Celular-Formato' : nameVerified[nameVerified.length] = 'Celular-Formato';
                    context.l10n_cl_dte_email ? valueEmail ? nameVerified[nameVerified.length] = 'Email_DTE' : nameVerified[nameVerified.length] = 'Email_DTE-Formato' :  nameVerified[nameVerified.length] = 'Email_DTE-Formato';
                    context.street ? nameVerified[nameVerified.length] = 'Calle' : nameVerified[nameVerified.length] = 'Calle-Formato';
                    context.city ? nameVerified[nameVerified.length] = 'Ciudad' : nameVerified[nameVerified.length] = 'Ciudad-Formato';
                    context.country_id ? nameVerified[nameVerified.length] = 'Pais' : nameVerified[nameVerified.length] = 'Pais-Formato';
                    context.state_id ? nameVerified[nameVerified.length] = 'Comuna' : nameVerified[nameVerified.length] = 'Comuna-Formato';
                    context.vat ? valueRut ? nameVerified[nameVerified.length] = 'RUT' : nameVerified[nameVerified.length] = 'RUT-Formato' : nameVerified[nameVerified.length] = 'RUT-Formato';
                    context.dob ? nameVerified[nameVerified.length] = 'Fecha de Nacimiento' : nameVerified[nameVerified.length] = 'Fecha de Nacimiento-Formato';
                    context.l10n_cl_sii_taxpayer_type ? nameVerified[nameVerified.length] = 'Tipo Contribuyente' : nameVerified[nameVerified.length] = 'Tipo Contribuyente-Formato';
                    context.l10n_cl_activity_description ? nameVerified[nameVerified.length] = 'Giro': nameVerified[nameVerified.length] = 'Giro-Formato';
                    }else{
                        nameVerified[nameVerified.length] = 'Telefono-Formato';
                        nameVerified[nameVerified.length] = 'Celular-Formato';
                        nameVerified[nameVerified.length] = 'Email_DTE-Formato';
                        nameVerified[nameVerified.length] = 'Calle-Formato';
                        nameVerified[nameVerified.length] = 'Ciudad-Formato';
                        nameVerified[nameVerified.length] = 'Pais-Formato';
                        nameVerified[nameVerified.length] = 'Comuna-Formato';
                        nameVerified[nameVerified.length] = 'RUT-Formato';
                        nameVerified[nameVerified.length] = 'Fecha de Nacimiento-Formato';
                        nameVerified[nameVerified.length] = 'Tipo Contribuyente-Formato';
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
                let valueEmail = rgEmail.test(data.l10n_cl_dte_email);
                console.log('parse -> ' + !isNaN(parseInt(data.phone)));
                console.log('val email -> ' + valueEmail);
                console.log('val tel -> ' + rgTel.test(data.phone));
                console.log('val cel -> ' + rgTel.test(data.mobile));
                console.log('val rut -> ' + rgRut.test(data.vat));
                console.log('ver tel -> ' + data.phone);
                console.log('ver cel -> ' + data.mobile);
                console.log('ver mail -> ' + data.l10n_cl_dte_email);
                console.log('ver rut -> ' + data.vat);
                if(data != null){
                    // data.phone === null || data.phone === '' || data.phone === undefined ? console.log(1) : (isNaN(parseInt(data.phone)) ? nameVerified[nameVerified.length] = 'Telefono-1' : nameVerified[nameVerified.length] = 'Telefono');
                    data.phone === null || data.phone === '' || data.phone === undefined ? console.log('verificacion changed 1') : valueTel ? nameVerified[nameVerified.length] = 'Telefono' : nameVerified[nameVerified.length] = 'Telefono-Formato';
                    data.mobile === null || data.mobile === '' || data.mobile === undefined ? console.log('verificacion changed 2') : valueCel ? nameVerified[nameVerified.length] = 'Celular' : nameVerified[nameVerified.length] = 'Celular-Formato';
                    data.l10n_cl_dte_email === null || data.l10n_cl_dte_email === '' || data.l10n_cl_dte_email === undefined ? console.log('verificacion changed 3') : valueEmail ? nameVerified[nameVerified.length] = 'Email_DTE' : 'Email_DTE-Formato';
                    data.street === null || data.street === '' || data.street === undefined ? console.log('verificacion changed 4') : nameVerified[nameVerified.length] = 'Calle';
                    data.city === null || data.city === '' || data.city === undefined ? console.log('verificacion changed 5') : nameVerified[nameVerified.length] = 'Ciudad';
                    data.country_id === null || data.country_id === '' || data.country_id === undefined || data.country_id === false? console.log('verificacion changed 6') : nameVerified[nameVerified.length] = 'Pais';
                    data.state_id === null || data.state_id === '' || data.state_id === undefined || data.state_id === false ? console.log('verificacion changed 7') : nameVerified[nameVerified.length] = 'Comuna';
                    data.vat === null || data.vat === '' || data.vat === undefined ? console.log('verificacion changed 8') : valueRut ? nameVerified[nameVerified.length] = 'RUT' : nameVerified[nameVerified.length] = 'RUT-1';
                    data.dob === null || data.dob === '' || data.dob === undefined ? console.log('verificacion changed 9') : nameVerified[nameVerified.length] = 'Fecha de Nacimiento';
                    data.l10n_cl_sii_taxpayer_type === null || data.l10n_cl_sii_taxpayer_type === '' || data.l10n_cl_sii_taxpayer_type === undefined ? console.log('verificacion changed 10 ') : nameVerified[nameVerified.length] = 'Tipo Contribuyente';
                    data.l10n_cl_activity_description === null || data.l10n_cl_activity_description === '' || data.l10n_cl_sii_taxpayer_type === undefined ? console.log('verificacion changed 11') : nameVerified[nameVerified.length] = 'Giro';
                    }
                nameVerified.length === 0 ? verified = true : verified = false;
                return { 'verified' : verified, 'nameVerified' : nameVerified};
            }

            async saveCustomer(event){
                let data = event.detail.processedChanges;
                if(data != null) {
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
                        //             compare = 'PE';
                        //             console.log('presente con error en -> ' + chan);
                        //         }else{
                                    compare = 'SD';
                                    // element = a[]
                                    console.log('aloja');
                                }
                            }
                        });
                        // if(compare === 'PS') {
                        //     compare = 'SD';
                        // }else{
                        //     compare = 'SD';
                        // }
                    }
                    compare === 'SD' ? '' : unifiedResponse[unifiedResponse.length] = element;
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
