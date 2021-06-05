odoo.define('ccu_pos.ClientDetailsEdit', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var utils = require('web.utils');

    const { useListener } = require('web.custom_hooks');
    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');

    models.load_fields('res.partner',['is_company','l10n_cl_activity_description']);
    // models.load_fields('res.partner','l10n_cl_activity_description');
    models.load_fields('res.partner','l10n_latam_identification_type_id');
    models.load_fields('res.partner','gender');
    models.load_fields('res.partner','dob');
    models.load_fields('res.partner','age');
    models.load_fields('res.partner','category');

    const ClientDetailsEditValidate = ClientDetailsEdit =>
        class extends ClientDetailsEdit {
            constructor() {
                super(...arguments);
                useListener('type-customer-validate', this.typeCustomerValidate);
            }
            get isCompany(){
                return this.props.partner.is_company;
            }

            giroEmpresa(){
                return this.env.props.partner.l10n_cl_activity_description;
            }
            async typeCustomerValidate(event) {
                if(event.getValue() === 'person' && this.isCompany){
                   const { confirmed, payload } = await this.showPopup('ConfirmPopup', {
                       title: this.env._t('Confirmación'),
                       body: this.env._t('Desea cambiar la modalidad del cliente a Persona.'),
                   });
                   if (confirmed) {
                       console.log(payload, 'payload')
                   }
                }if(event.getValue() === 'company' && !this.isCompany){
                   const { confirmed, payload } = await this.showPopup('ConfirmPopup', {
                       title: this.env._t('Confirmación'),
                       body: this.env._t('Desea cambiar la modalidad del cliente a Empresa.'),
                   });
                   if (confirmed) {
                       console.log(payload, 'payload')
                   }
                }
                this.render();
            }
            _is_valid_age(){
                if(18 <= this.prop.partner.age <= 120){
                    return true;
                }else{
                    return false;
                }
            }
        }

    Registries.Component.extend(ClientDetailsEdit, ClientDetailsEditValidate);

    return ClientDetailsEdit;

});
