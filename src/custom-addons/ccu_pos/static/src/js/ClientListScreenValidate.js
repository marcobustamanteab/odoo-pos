odoo.define('ccu_pos.ClientListScreenValidate', function (require) {
    "use strict";

    const framework = require('web.framework');
    const { useListener } = require('web.custom_hooks');
    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Registries = require('point_of_sale.Registries');

    const ClientListScreenValidate = ClientListScreen =>
        class extends ClientListScreen {
            constructor() {
                super(...arguments);
                useListener('click-refresh', this.clickRefresh);
                useListener('click-save-transbank', this.saveCustomer);
                useListener('activate-pos-clear', this.activateEditClear);
            }
            async clickRefresh(){
                await this.env.pos.load_new_partners();
                // create_from_ui
            }
            get refreshButton(){
                return { command: 'refresh', text: 'Refrescar Cliente' };
            }

            async clickSaveTransbank(){

                var domain = [['id', '=', '9963']];
                this.rpc({
                    model: 'res.partner',
                    method: 'search_read',
                    args: [domain],
                    kwargs: { limit: 5 },
                }).then(function (partner) {
                    if (partner.length > 0) {
                        for(var i=0; i<partner.length;i++){
                            console.log(partner[0].name);
                            console.log(JSON.stringify(partner));
                        }
                    } else {
                        self.showPopup('ErrorPopup', { body: 'No previous orders found' });
                    }
                });
                // return rpcProm;


                // const context = this.state.editModeProps.partner;
                // if(this.changes != null){
                //     const change = this.changes;
                //     context.country_id = change.country_id;
                //     context.state_id = change.state_id;
                //     context.name = change.name;
                //     context.street = change.street;
                //     context.city = change.city;
                //     context.email = change.email;
                //     context.phone = change.phone;
                //     context.dob = change.dob;
                //     context.email = change.email;
                //
                // }
                //
                // // const context = this.props;
                // if (context.is_company && !context.name || !context.vat
                //     || !context.l10n_cl_activity_description || !context.l10n_cl_sii_taxpayer_type
                //     || !context.address || !context.city || !context.country_id || !context.state_id){
                //         return this.showPopup('ErrorPopup', {
                //           title: ('Ingrese los datos requeridos'),
                //         });
                // } else if (!context.is_company && !context.name || !context.address
                //     || !context.city || !context.country_id || !context.state_id){
                //         return this.showPopup('ErrorPopup', {
                //           title: ('Ingrese los datos requeridos'),
                //         });
                // } else {
                //     this.env.bus.trigger('save-customer');
                // }
            }
            async saveCustomer(){
                // var domain = [['id', '=', '9963']];
                console.log(JSON.stringify(this.getClienteTemplate()))
                this.rpc({
                    model: 'res.partner',
                    method: 'create',
                    args: [this.getClienteTemplate()],
                    kwargs: {},
                }).then(function (partner) {
                    if (partner.length > 0) {
                        console.log(partner);
                    } else {
                        console.log(partner);
                    }
                });
            }
            getClienteTemplate() {
               return {
	"display_name": "juan perez",
	"date": false,
	"title": false,
	"parent_id": false,
	"parent_name": false,
	"child_ids": [],
	"ref": false,
	"lang": "es_CL",
	"active_lang_count": 1,
	"tz": "America/Santiago",
	"tz_offset": "-0400",
	"same_vat_partner_id": false,
	"bank_ids": [],
	"website": false,
	"comment": false,
	"category_id": [],
	"credit_limit": 0,
	"active": true,
	"employee": false,
	"function": false,
	"type": "contact",
	"street2": false,
	"zip": false,
	"city": "LAS CONDES",
	"state_id": 1183,
	"country_id": 46,
	"partner_latitude": 0,
	"partner_longitude": 0,
	"email_formatted": "juan.perez123@1.cl",
	"is_company": true,
	"industry_id": false,
	"company_type": "company",
	"company_id": false,
	"color": 0,
	"user_ids": [],
	"partner_share": true,
	"contact_address": "juan perez",
	"commercial_partner_id": [],
	"commercial_company_name": "juan perez",
	"company_name": false,
	"barcode": false,
	"self": [],
	"country_enforce_cities": false,
	"city_id": false,
	"im_status": "im_partner",
	"activity_ids": [],
	"activity_state": false,
	"activity_user_id": false,
	"activity_type_id": false,
	"activity_type_icon": false,
	"activity_date_deadline": false,
	"my_activity_date_deadline": false,
	"activity_summary": false,
	"activity_exception_decoration": false,
	"activity_exception_icon": false,
	"message_is_follower": false,
	"message_follower_ids": [],
	"message_partner_ids": [],
	"message_channel_ids": [],
	"message_ids": [],
	"message_unread": false,
	"message_unread_counter": 0,
	"message_needaction": false,
	"message_needaction_counter": 0,
	"message_has_error": false,
	"message_has_error_counter": 0,
	"message_attachment_count": 0,
	"message_main_attachment_id": false,
	"email_normalized": "123@1.cl",
	"is_blacklisted": false,
	"message_bounce": 0,
	"phone": "123",
	"channel_ids": [],
	"user_id": false,
	"contact_address_complete": "holanda q talca",
	"image_medium": false,
	"signup_token": false,
	"signup_type": false,
	"signup_expiration": false,
	"signup_valid": false,
	"signup_url": false,
	"phone_sanitized": "+56 9 7894 4561",
	"phone_sanitized_blacklisted": false,
	"phone_blacklisted": false,
	"mobile_blacklisted": false,
	"property_product_pricelist": 1,
	"team_id": false,
	"website_message_ids": [],
	"email": "juan.perez123@1.cl",
	"mobile": "+56 9 7894 4561",
	"name": "juan perez",
	"street": "VITACURA 2670",
	"gender": "male",
	"category": "copero",
	"status": "unconfirmed",
	"dob": "1980-01-01",
	"age": 41,
	"limit_purchase": 500000,
	"monthly_purchase": 0,
	"reached_limit": false,
	"is_employee": false,
	"distribution_center": false,
	"ocn_token": false,
	"partner_gid": 0,
	"additional_info": false,
	"message_has_sms_error": false,
	"credit": 0,
	"debit": 0,
	"debit_limit": 0,
	"total_invoiced": 0,
	"currency_id": 45,
	"journal_item_count": 78,
	"property_account_payable_id": 493,
	"property_account_receivable_id": 418,
	"property_account_position_id": false,
	"property_payment_term_id": false,
	"property_supplier_payment_term_id": false,
	"ref_company_ids": [],
	"has_unreconciled_entries": false,
	"last_time_entries_checked": false,
	"invoice_ids": [],
	"contract_ids": [],
	"bank_account_count": 0,
	"trust": "normal",
	"invoice_warn": "no-message",
	"invoice_warn_msg": false,
	"supplier_rank": 0,
	"customer_rank": 0,
	"property_stock_customer": 5,
	"property_stock_supplier": 4,
	"picking_warn": "no-message",
	"picking_warn_msg": false,
	"online_partner_vendor_name": false,
	"online_partner_bank_account": false,
	"payment_token_ids": [],
	"payment_token_count": 0,
	"online_partner_information": false,
	"l10n_latam_identification_type_id": 4,
	"vat": "13524308-6",
	"pos_order_count": 0,
	"pos_order_ids": [],
	"sale_order_count": 0,
	"sale_order_ids": [],
	"sale_warn": "no-message",
	"sale_warn_msg": false,
	"payment_next_action_date": false,
	"unreconciled_aml_ids": [],
	"unpaid_invoices": [],
	"total_due": 0,
	"total_overdue": 0,
	"followup_status": "in_need_of_action",
	"followup_level": 3,
	"payment_responsible_id": false,
	"l10n_cl_sii_taxpayer_type": "3",
	"loyalty_points": 0,
	"image_1920": false,
	"image_1024": false,
	"image_512": false,
	"image_256": false,
	"image_128": false,
	"l10n_cl_dte_email": "juan.perez.dte@1.cl",
	"l10n_cl_activity_description": "CONSUMIDOR FINAL"
};
//                {
// 	"id" : 9963,
// 	"display_name": "ADWENS  CASSEUS",
// 	"date": false,
// 	"title": false,
// 	"parent_id": false,
// 	"parent_name": false,
// 	"child_ids": [10165],
// 	"ref": false,
// 	"lang": "es_CL",
// 	"active_lang_count": 1,
// 	"tz": "America/Santiago",
// 	"tz_offset": "-0400",
// 	"same_vat_partner_id": false,
// 	"bank_ids": [],
// 	"website": false,
// 	"comment": false,
// 	"category_id": [],
// 	"credit_limit": 0,
// 	"active": true,
// 	"employee": false,
// 	"function": false,
// 	"type": "contact",
// 	"street2": false,
// 	"zip": false,
// 	"city": "LAS CONDES",
// 	"state_id": [1183, "Metropolitana (CL)"],
// 	"country_id": [46, "Chile"],
// 	"partner_latitude": 0,
// 	"partner_longitude": 0,
// 	"email_formatted": "\"ADWENS  CASSEUS\" <123@1.cl>",
// 	"is_company": true,
// 	"industry_id": false,
// 	"company_type": "company",
// 	"company_id": false,
// 	"color": 0,
// 	"user_ids": [],
// 	"partner_share": true,
// 	"contact_address": "ADWENS  CASSEUS\nVITACURA 2670\n\nLAS CONDES 13 \nChile",
// 	"commercial_partner_id": [9963, "ADWENS  CASSEUS"],
// 	"commercial_company_name": "ADWENS  CASSEUS",
// 	"company_name": false,
// 	"barcode": false,
// 	"self": [9963, "ADWENS  CASSEUS"],
// 	"country_enforce_cities": false,
// 	"city_id": false,
// 	"im_status": "im_partner",
// 	"activity_ids": [],
// 	"activity_state": false,
// 	"activity_user_id": false,
// 	"activity_type_id": false,
// 	"activity_type_icon": false,
// 	"activity_date_deadline": false,
// 	"my_activity_date_deadline": false,
// 	"activity_summary": false,
// 	"activity_exception_decoration": false,
// 	"activity_exception_icon": false,
// 	"message_is_follower": false,
// 	"message_follower_ids": [],
// 	"message_partner_ids": [],
// 	"message_channel_ids": [],
// 	"message_ids": [2323],
// 	"message_unread": false,
// 	"message_unread_counter": 0,
// 	"message_needaction": false,
// 	"message_needaction_counter": 0,
// 	"message_has_error": false,
// 	"message_has_error_counter": 0,
// 	"message_attachment_count": 0,
// 	"message_main_attachment_id": false,
// 	"email_normalized": "123@1.cl",
// 	"is_blacklisted": false,
// 	"message_bounce": 0,
// 	"phone": "123",
// 	"channel_ids": [],
// 	"user_id": false,
// 	"contact_address_complete": "VITACURA 2670, LAS CONDES, Metropolitana, Chile",
// 	"image_medium": false,
// 	"signup_token": false,
// 	"signup_type": false,
// 	"signup_expiration": false,
// 	"signup_valid": false,
// 	"signup_url": false,
// 	"phone_sanitized": "+56 9 7894 4561",
// 	"phone_sanitized_blacklisted": false,
// 	"phone_blacklisted": false,
// 	"mobile_blacklisted": false,
// 	"property_product_pricelist": [1, "Tarifa pública (CLP)"],
// 	"team_id": false,
// 	"website_message_ids": [],
// 	"email": "123@1.cl",
// 	"mobile": "+56 9 7894 4561",
// 	"name": "ADWENS  CASSEUS",
// 	"street": "VITACURA 2670",
// 	"gender": "male",
// 	"category": "copero",
// 	"status": "unconfirmed",
// 	"dob": "1980-01-01",
// 	"age": 41,
// 	"limit_purchase": 500000,
// 	"monthly_purchase": 0,
// 	"reached_limit": false,
// 	"is_employee": false,
// 	"distribution_center": false,
// 	"ocn_token": false,
// 	"partner_gid": 0,
// 	"additional_info": false,
// 	"message_has_sms_error": false,
// 	"credit": 157496,
// 	"debit": 0,
// 	"debit_limit": 0,
// 	"total_invoiced": 381390,
// 	"currency_id": [45, "CLP"],
// 	"journal_item_count": 78,
// 	"property_account_payable_id": [493, "210210 Proveedores"],
// 	"property_account_receivable_id": [418, "1103010005 Clientes"],
// 	"property_account_position_id": false,
// 	"property_payment_term_id": false,
// 	"property_supplier_payment_term_id": false,
// 	"ref_company_ids": [],
// 	"has_unreconciled_entries": false,
// 	"last_time_entries_checked": false,
// 	"invoice_ids": [224, 222, 220, 218, 213, 212, 204, 191, 190, 186, 185, 182, 169, 166, 115, 114, 112],
// 	"contract_ids": [],
// 	"bank_account_count": 0,
// 	"trust": "normal",
// 	"invoice_warn": "no-message",
// 	"invoice_warn_msg": false,
// 	"supplier_rank": 0,
// 	"customer_rank": 19,
// 	"property_stock_customer": [5, "Partner Locations/Customers"],
// 	"property_stock_supplier": [4, "Partner Locations/Vendors"],
// 	"picking_warn": "no-message",
// 	"picking_warn_msg": false,
// 	"online_partner_vendor_name": false,
// 	"online_partner_bank_account": false,
// 	"payment_token_ids": [],
// 	"payment_token_count": 0,
// 	"online_partner_information": false,
// 	"l10n_latam_identification_type_id": [4, "RUT"],
// 	"vat": "24977883-4",
// 	"pos_order_count": 16,
// 	"pos_order_ids": [160, 159, 158, 157, 156, 155, 147, 128, 127, 126, 124, 123, 122, 118, 117, 59],
// 	"sale_order_count": 0,
// 	"sale_order_ids": [],
// 	"sale_warn": "no-message",
// 	"sale_warn_msg": false,
// 	"payment_next_action_date": false,
// 	"unreconciled_aml_ids": [677, 678],
// 	"unpaid_invoices": [114, 112],
// 	"total_due": 157496,
// 	"total_overdue": 157496,
// 	"followup_status": "in_need_of_action",
// 	"followup_level": [3, "First Reminder"],
// 	"payment_responsible_id": false,
// 	"l10n_cl_sii_taxpayer_type": "3",
// 	"loyalty_points": 0,
// 	"image_1920": false,
// 	"image_1024": false,
// 	"image_512": false,
// 	"image_256": false,
// 	"image_128": false,
// 	"create_uid": [2, "Administrator"],
// 	"create_date": "2021-02-26 03:29:41",
// 	"write_uid": [2, "Administrator"],
// 	"write_date": "2021-06-30 01:04:40",
// 	"__last_update": "2021-06-30 01:04:40",
// 	"l10n_cl_dte_email": "adwens@gmail.com",
// 	"l10n_cl_activity_description": "CONSUMIDOR FINAL"
// };
            }
            
            activateEditClear(){
                console.log("aqui");
                this.state.editModeProps = {
                    partner: null,
                };
                this.env.bus.trigger('activate-edit-mode', { isNewClient: true });
            }
        }

    Registries.Component.extend(ClientListScreen, ClientListScreenValidate);

    return ClientListScreen;

});
