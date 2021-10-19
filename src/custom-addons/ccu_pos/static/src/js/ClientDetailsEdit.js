odoo.define('ccu_pos.ClientDetailsEdit', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    const { _t } = require('web.core');
    const { useListener } = require('web.custom_hooks');
    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');
    const Registries = require('point_of_sale.Registries');

    models.load_fields('res.partner',['is_company','l10n_cl_activity_description','gender','dob','age','category','l10n_cl_sii_taxpayer_type','l10n_cl_dte_email']);

    const ClientDetailsEditValidate = ClientDetailsEdit =>
        class extends ClientDetailsEdit {
            constructor() {
                super(...arguments);
                useListener('person-type-validate', this.personTypeValidate);
                useListener('company-type-validate', this.companyTypeValidate);
                // useListener('prepare-customer-pos', this.saveCustomerPos);
                this.clientePos = {
                    'changesPos' : {},
                    'partnerPos' : {},
                };
                this.props.clientePos = this.clientePos;
                this.props.parameters = this.config();
                if(this.props.partner.l10n_cl_sii_taxpayer_type != '' && this.props.partner.l10n_cl_sii_taxpayer_type){
                    this.props.partner.l10n_cl_sii_taxpayer_type = parseInt(this.props.partner.l10n_cl_sii_taxpayer_type);
                }
                let objLength = Object.keys(this.props.partner).length;
                if(objLength === 2 && this.props.partner.country_id[0] === 46 && this.props.partner.state_id[0] === 1183){
                    console.log('validacion cliente nuevo ');
                    this.props.partner.country_id = false;
                    this.props.partner.state_id = false;
                }
            }
            mounted() {
                this.env.bus.on('prepare-customer-pos', this, this.saveCustomerPos);
            }
            willUnmount() {
                this.env.bus.off('prepare-customer-pos', this);
            }
            config(){
               return {
                    'taxpayer' : [
                        {
                            'name' : 'Seleccione Tipo',
                            'value': 0
                        },
                        {
                            'name' : 'IVA afecto 1ª categoría',
                            'value': 1
                        },
                        {
                            'name' : 'Emisor de boleta 2da categoría',
                            'value': 2
                        },
                        {
                            'name' : 'Consumidor final',
                            'value': 3
                        },
                        {
                            'name' : 'Extranjero',
                            'value': 4
                        }
                    ]
                };
            }
            giroEmpresa() {
                return this.env.props.partner.l10n_cl_activity_description;
            }

            async personTypeValidate(event) {
                this.props.partner.is_company = false;
                this.render();
            }

            async companyTypeValidate(event) {
                this.props.partner.is_company = true;
                this.render();
            }

            isValidAge() {
                if (18 <= this.props.partner.age <= 120) {
                    return true;
                } else {
                    return false;
                }
            }

            get customerTrx() {
                return this.env.pos.states;
            }
            refreshStatesPos(event) {
                this.render();
            }

            captureChange2(event) {
                this.changes[event.target.name] = event.target.value;
                this.clientePos.changesPos[event.target.name] = event.target.value;
                this.props.clientePos = this.clientePos;
            }

            saveCustomerPos(event) {
                let processedChanges = {};
                for (let [key, value] of Object.entries(this.changes)) {
                    if (this.intFields.includes(key)) {
                        processedChanges[key] = parseInt(value) || false;
                    } else {
                        processedChanges[key] = value;
                    }
                }
                if ((!this.props.partner.name && !processedChanges.name) ||
                    processedChanges.name === '' ){
                    return this.showPopup('ErrorPopup', {
                      title: _t('Debe ingresar un nombre del cliente'),
                    });
                }
                processedChanges.id = this.props.partner.id || false;
                this.trigger('save-customer-pos', { processedChanges } );
            }
            readCustomerExtra(part){
                let ids = part.id;
                let partners = this.env.pos.partners;
                let partner = null;
                for(var i=0;i<partners.length;i++){
                    if(ids === partners[i].id){
                        partner = partners[i];
                    }
                }
                // this.props.clientePos.l10n_cl_sii_taxpayer_type = partner.l10n_cl_sii_taxpayer_type;
                this.props.partner.l10n_cl_sii_taxpayer_type = partner.l10n_cl_sii_taxpayer_type;
            }

     }

            Registries.Component.extend(ClientDetailsEdit, ClientDetailsEditValidate);

            return ClientDetailsEdit;
});
