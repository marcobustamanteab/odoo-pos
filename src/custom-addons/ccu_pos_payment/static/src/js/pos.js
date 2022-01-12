odoo.define('pos_chque_information.pos', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var core = require('web.core');
	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const { useListener } = require('web.custom_hooks');
	const Registries = require('point_of_sale.Registries');
	var QWeb = core.qweb;

	var _t = core._t;


	models.load_models({
		model:  'pos.payment.method',
		fields: ['name', 'is_cash_count', 'use_payment_terminal', 'cheque_information'],
		domain: function(self, tmp) {
			return [['id', 'in', tmp.payment_method_ids]];
		},
		loaded: function(self, payment_methods) {
			self.payment_methods = payment_methods.sort(function(a,b){
				// prefer cash payment_method to be first in the list
				if (a.is_cash_count && !b.is_cash_count) {
					return -1;
				} else if (!a.is_cash_count && b.is_cash_count) {
					return 1;
				} else {
					return a.id - b.id;
				}
			});
			self.payment_methods_by_id = {};
			_.each(self.payment_methods, function(payment_method) {
				self.payment_methods_by_id[payment_method.id] = payment_method;

				var PaymentInterface = self.electronic_payment_interfaces[payment_method.use_payment_terminal];
				if (PaymentInterface) {
					payment_method.payment_terminal = new PaymentInterface(self, payment_method);
				}
			});
		}
	});

	var posorder_super = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function(attr, options) {
			posorder_super.initialize.apply(this,arguments);
			this.vat = this.vat || false;
			this.owner_name = this.owner_name || false;
			this.check_date = this.check_date || false;
			this.cheque_number = this.cheque_number || false;
		},

		export_as_JSON: function() {
			var json = posorder_super.export_as_JSON.apply(this,arguments);
			json.vat = this.vat;
			json.owner_name = this.owner_name;
			json.check_date = this.check_date;
			json.cheque_number = this.cheque_number;

			return json;
		},
		init_from_JSON: function(json) {
			posorder_super.init_from_JSON.apply(this,arguments);
			this.vat = json.vat;
			this.owner_name = json.owner_name;
			this.check_date = json.check_date;
			this.cheque_number = json.cheque_number;
		},
		get_owner_name:function() {
			return this.owner_name
		},
		set_owner_name:function(owner_name) {
			this.owner_name = owner_name
			this.trigger('change');
		},
		get_vat:function() {
			return this.vat
		},
		set_vat:function(vat) {
			this.vat = vat
			this.trigger('change');
		},

		get_check_date:function() {
			return this.check_date
		},
		set_check_date:function(check_date) {
			this.check_date = check_date
			this.trigger('change');
		},

		get_cheque_number:function() {
			return this.cheque_number
		},
		set_cheque_number:function(cheque_number) {
			this.cheque_number = cheque_number
			this.trigger('change');
		},

	});

	const PosChequePaymentScreen = (PaymentScreen) =>
		class extends PaymentScreen {
			constructor() {
				super(...arguments);
				useListener('cheque-bank', this.chequeinformation);
			}
			chequeinformation(event) {
				let self = this;
				this.showPopup('ChequeInformationPopup', {
					body: 'Cheque',
					startingValue: self,
					list: self.env.pos.bank,
                    title: this.env._t('Information'),
                });
			}
		};

	Registries.Component.extend(PaymentScreen, PosChequePaymentScreen);

	return PosChequePaymentScreen;
});
