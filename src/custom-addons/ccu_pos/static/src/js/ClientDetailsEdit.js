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
                useListener('save-changes-pos', this.saveCustomerPos);
                this.clientePos = this.props.partner;
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
                var context = this.props;
                this.clientePos = context.partner;
                console.log("antes" + context.partner[event.target.name]);
                context.partner[event.target.name] = event.target.value;
                console.log("despues" + context.partner[event.target.name]);
            }

            saveCustomerPos(processedChanges) {

                // let processedChanges = {};
                for (let [key, value] of Object.entries(this.changes)) {
                    if (this.intFields.includes(key)) {
                        processedChanges[key] = parseInt(value) || false;
                    } else {
                        processedChanges[key] = value;
                    }
                }
                if ((!this.props.partner.name && !processedChanges.name) ||
                    processedChanges.name === '') {
                    return this.showPopup('ErrorPopup', {
                        title: _t('A Customer Name Is Required'),
                    });
                }

                // console.log(JSON.stringify(this.getClienteTemplate()))
                this.rpc({
                    model: 'res.partner',
                    method: 'create',
                    args: [this.getClienteTemplate(processedChanges)],
                    kwargs: {},
                }).then(function (partner) {
                    if (partner.length > 0) {
                        console.log(partner);
                    } else {
                        console.log("error!!!");
                    }
                });
            }

            getClienteTemplate(processedChanges) {
                return {
                    "display_name": processedChanges.name ? processedChanges.name : this.props.partner.name,
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
                    "city": processedChanges.city ? processedChanges.city : this.props.partner.city,
                    "state_id": 1183,
                    "country_id": 46,
                    "partner_latitude": 0,
                    "partner_longitude": 0,
                    "email_formatted": processedChanges.email ? processedChanges.email : this.props.partner.email,
                    "is_company": true,
                    "industry_id": false,
                    "company_type": "company",
                    "company_id": false,
                    "color": 0,
                    "user_ids": [],
                    "partner_share": true,
                    "contact_address": processedChanges.name ? processedChanges.name : this.props.partner.name,
                    "commercial_partner_id": [],
                    "commercial_company_name": processedChanges.name ? processedChanges.name : this.props.partner.name,
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
                    "email_normalized": processedChanges.email ? processedChanges.email : this.props.partner.email,
                    "is_blacklisted": false,
                    "message_bounce": 0,
                    "phone": processedChanges.phone ? processedChanges.phone : this.props.partner.phone,
                    "channel_ids": [],
                    "user_id": false,
                    "contact_address_complete": processedChanges.street ? processedChanges.street : this.props.partner.street,
                    "image_medium": false,
                    "signup_token": false,
                    "signup_type": false,
                    "signup_expiration": false,
                    "signup_valid": false,
                    "signup_url": false,
                    "phone_sanitized": processedChanges.phone ? processedChanges.phone : this.props.partner.phone,
                    "phone_sanitized_blacklisted": false,
                    "phone_blacklisted": false,
                    "mobile_blacklisted": false,
                    "property_product_pricelist": 1,
                    "team_id": false,
                    "website_message_ids": [],
                    "email": processedChanges.email ? processedChanges.email : this.props.partner.email,
                    "mobile": processedChanges.mobile ? processedChanges.mobile : this.props.partner.mobile,
                    "name": processedChanges.name ? processedChanges.name : this.props.partner.name,
                    "street": processedChanges.street ? processedChanges.street : this.props.partner.street,
                    "gender": "male",
                    "category": "copero",
                    "status": "unconfirmed",
                    "dob": processedChanges.dob ? processedChanges.dob : this.props.partner.dob,
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
                    "l10n_cl_sii_taxpayer_type": processedChanges.l10n_cl_sii_taxpayer_type ? processedChanges.l10n_cl_sii_taxpayer_type : this.props.partner.l10n_cl_sii_taxpayer_type,
                    "loyalty_points": 0,
                    "image_1920": false,
                    "image_1024": false,
                    "image_512": false,
                    "image_256": false,
                    "image_128": false,
                    "l10n_cl_dte_email": processedChanges.email ? processedChanges.email : this.props.partner.email,
                    "l10n_cl_activity_description": processedChanges.l10n_cl_activity_description ? processedChanges.l10n_cl_activity_description : this.props.partner.l10n_cl_activity_description
                };


            }
     }

            Registries.Component.extend(ClientDetailsEdit, ClientDetailsEditValidate);

            return ClientDetailsEdit;
});
