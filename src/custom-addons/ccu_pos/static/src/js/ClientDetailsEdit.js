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
            }
            mounted() {
                this.env.bus.on('prepare-customer-pos', this, this.saveCustomerPos);
            }
            willUnmount() {
                this.env.bus.off('prepare-customer-pos', this);
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
                // let processedChanges = {};
                // for (let [key, value] of Object.entries(this.changes)) {
                //     if (this.intFields.includes(key)) {
                //         processedChanges[key] = parseInt(value) || false;
                //     } else {
                //         processedChanges[key] = value;
                //     }
                // }
                // if ((!this.props.partner.name && !processedChanges.name) ||
                //     processedChanges.name === '') {
                //     return this.showPopup('ErrorPopup', {
                //         title: _t('A Customer Name Is Required'),
                //     });
                // }

                // console.log(JSON.stringify(this.getClienteTemplate()))

            }


     }

            Registries.Component.extend(ClientDetailsEdit, ClientDetailsEditValidate);

            return ClientDetailsEdit;
});
