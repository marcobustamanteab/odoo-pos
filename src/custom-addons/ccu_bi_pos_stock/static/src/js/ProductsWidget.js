// CCU BiProductScreen js
odoo.define('ccu_bi_pos_stock.ProductsWidget', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ProductsWidget = require('bi_pos_stock.ProductsWidget');

	let prd_list_count = 0;

	const CCUBiProductsWidget = (ProductsWidget) =>
		class extends ProductsWidget {
			constructor() {
				super(...arguments);
			}

			mounted() {
				super.mounted();
				this.env.pos.on('change:is_sync', this.render, this);
			}

			willUnmount() {
				super.willUnmount();
				this.env.pos.off('change:is_sync', null, this);
			}

			get productsToDisplay() {

				let self = this;
				let prods = super.productsToDisplay;

				if ((self.env.pos.config.show_stock_location == 'specific') && (self.env.pos.config.pos_deny_order == 0) && !(self.env.pos.config.pos_allow_order)) {
					let prod_ids = [];
					// let x_sync = self.env.pos.get("is_sync");
					// let location = self.env.pos.locations;
					// if(x_sync == true || !("bi_on_hand" in prods) || !("bi_available" in prods)) {
						if (self.env.pos.config.pos_stock_type == 'onhand') {
							$.each(prods, function(i, prd) {
								let val = { prods_index:i, id:prd.id, qty:prd.bi_on_hand, type:prd.type };
								prod_ids.push(val);
							});
						}
						if (self.env.pos.config.pos_stock_type == 'available') {
							$.each(prods, function(i, prd) {
								let val = { prods_index:i, id:prd.id, qty:prd.bi_available, type:prd.type };
								prod_ids.push(val);
							});
						}
						for (let i = prod_ids.length - 1; i >= 0; i--) {
							if ((prod_ids[i].type != 'service') && (prod_ids[i].qty <= 0) && (prod_ids[i].prods_index >= 0)) {
								prods.splice(prod_ids[i].prods_index, 1);
							}
						};
						// self.env.pos.set("is_sync",false);
					// }
				}
				return prods
			}
		};

	Registries.Component.extend(ProductsWidget, CCUBiProductsWidget);

	return ProductsWidget;

});
