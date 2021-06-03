odoo.define('ccu_pos.ClientDetailsEdit', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var utils = require('web.utils');

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
                // useListener('save-payment-line', this.validateOrderTransbank);
            }
            isCompany(){
                return this.env.props.partner.is_company;
            }
            // get TransactionName(){
            //     return this.get_client();
            // }
            giroEmpresa(){
                return this.env.props.partner.l10n_cl_activity_description;
            }
            // validateOrderTransbank(event) {
            //     if(this.env.pos.attributes.selectedOrder.paymentlines.models[0].transaction_id > 99999){
            //         this.validateOrder(false);
            //     }
            //     this.render();
            // }
        }

    Registries.Component.extend(ClientDetailsEdit, ClientDetailsEditValidate);

    return ClientDetailsEdit;

});
