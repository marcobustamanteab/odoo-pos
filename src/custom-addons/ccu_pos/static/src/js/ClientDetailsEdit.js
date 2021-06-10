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
            }
            giroEmpresa(){
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
            isValidAge(){
                if(18 <= this.props.partner.age <= 120){
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
        }

    Registries.Component.extend(ClientDetailsEdit, ClientDetailsEditValidate);

    return ClientDetailsEdit;

});
