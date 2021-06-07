odoo.define('ccu_pos.ClientDetailsEdit', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var utils = require('web.utils');

    const { useListener } = require('web.custom_hooks');
    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');

    models.load_fields('res.partner',['is_company','l10n_cl_activity_description','gender','dob','age','category','l10n_cl_sii_taxpayer_type']);

    const ClientDetailsEditValidate = ClientDetailsEdit =>
        class extends ClientDetailsEdit {
            constructor() {
                super(...arguments);
                useListener('type-customer-validate', this.typeCustomerValidate);
                useListener('person-type-validate', this.personTypeValidate);
                useListener('company-type-validate', this.companyTypeValidate);
                useListener('click-refresh', this.clickRefresh);
            }
            get isCompany(){
                if(this.props.partner.is_company){
                    this.props.conditionCompany = true;
                    this.props.conditionPerson = false;
                    this.props.conditionHiddenFields = false;
                }else{
                    this.props.conditionCompany = false;
                    this.props.conditionPerson = true;
                    this.props.conditionHiddenFields = true;
                }
                return this.props.partner.is_company;
            }
            giroEmpresa(){
                return this.env.props.partner.l10n_cl_activity_description;
            }
            async typeCustomerValidate(event) {
                var self = this;
                const {isCompany} = event.detail;
                const {confirmed, payload} = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Confirm Popup'),
                    body: this.env._t('This click is successfully done.'),
                });
                if (confirmed) {
                    // console.log(payload, 'payload')
                    this.props.conditionCompany = false;
                    this.props.conditionPerson = true;
                }
            }
            async personTypeValidate(event) {
                var self = this;
                const {isCompany} = event.detail;
                const {confirmed, payload} = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Confirmar Acción'),
                    body: this.env._t('Desea cambiar la configuración de cliente persona.'),
                });
                if (confirmed) {
                    // console.log(payload, 'person')
                    this.props.conditionCompany = false;
                    this.props.conditionPerson = true;
                }else{
                    this.props.conditionCompany = true;
                    this.props.conditionPerson = false;
                }
            }
            async companyTypeValidate(event) {
                var self = this;
                const {isCompany} = event.detail;
                const {confirmed, payload} = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Confirmar Acción'),
                    body: this.env._t('Desea cambiar la configuración de cliente empresa.'),
                });
                if (confirmed) {
                    // console.log(payload, 'company')
                    this.props.conditionCompany = true;
                    this.props.conditionPerson = false;
                }else{
                    this.props.conditionCompany = true;
                    this.props.conditionPerson = false;
                }
            }
            isValidAge(){
                if(18 <= this.prop.partner.age <= 120){
                    return true;
                }else{
                    return false;
                }
            }
            checkCompany(condition){
                return condition;
            }
            checkPerson(condition){
                return condition;
            }
            async clickRefresh() {
               var self = this;
               const { confirmed, payload } = await this.showPopup('NumberPopup', {
                   title: this.env._t('Number Popup'),
                   body: this.env._t('This click is successfully done.'),
               });
               if (confirmed) {
                   console.log(payload, 'payload')
               }
            }
        }

    Registries.Component.extend(ClientDetailsEdit, ClientDetailsEditValidate);

    return ClientDetailsEdit;

});
