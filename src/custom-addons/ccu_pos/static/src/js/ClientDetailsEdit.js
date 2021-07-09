odoo.define('ccu_pos.ClientDetailsEdit', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    const { useListener } = require('web.custom_hooks');
    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');
    const Registries = require('point_of_sale.Registries');

    models.load_fields('res.partner',['is_company','l10n_cl_activity_description','gender','dob','age','category','l10n_cl_sii_taxpayer_type']);

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
                // this.readCustomerExtra(this.props.partner);
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
                console.log('holanda');
                let processedChanges = this.clientePos;
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
