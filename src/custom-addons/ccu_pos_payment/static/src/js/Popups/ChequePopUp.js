odoo.define('pos_cheque_information.ChequePopup', function(require) {
	"use strict";

	var core = require('web.core');
	const { useState, useRef } = owl.hooks;
	const { useListener } = require('web.custom_hooks');
	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
	var QWeb = core.qweb;

	var _t = core._t;

	class ChequeInformationPopup extends AbstractAwaitablePopup {
		constructor() {
			super(...arguments);
			this.inputselectedeRef = useRef('input-selected');
			this.inputNameRef = useRef('input-name');
			this.inputVatRef = useRef('input-vat');
			this.inputaccountRef = useRef('input-account');
			this.inputnumberRef = useRef('input-number');

		}
		mounted() {
            this.inputVatRef.el.focus();
        }

        getValue() {
        	var order = this.env.pos.get_order()
			order.set_vat(this.inputVatRef.el.value);
			order.set_owner_name(this.inputNameRef.el.value);
			order.set_check_date(this.inputaccountRef.el.value);
			order.set_cheque_number(this.inputnumberRef.el.value);
			this.trigger('close-popup');
        }
        cancel() {
        	this.trigger('close-popup');
        }
	}

	ChequeInformationPopup.template = 'ChequeInformationPopup';
	ChequeInformationPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',
        list: [],
        startingValue: '',
    };

	Registries.Component.add(ChequeInformationPopup);

	return ChequeInformationPopup;
});
