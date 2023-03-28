odoo.define('ccu_pos.CCUProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const NumberBuffer = require('point_of_sale.NumberBuffer');

    const CCUProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _clickProduct(event) {
                if (!await this.validateOrderQuantities(1)){
                    return false
                }
                if (!this.currentOrder) {
                    this.env.pos.add_new_order();
                }
                const product = event.detail;
                const options = await this._getAddProductOptions(product);
                // Do not add product if options is undefined.
                if (!options) return;
                // Add the product after having the extra information.
                this.currentOrder.add_product(product, options);
                NumberBuffer.reset();
            }

            async _updateSelectedOrderline(event) {
                if(this.state.numpadMode === 'quantity' && this.env.pos.disallowLineQuantityChange()) {
                    let order = this.env.pos.get_order();
                    let selectedLine = order.get_selected_orderline();
                    let lastId = order.orderlines.last().cid;
                    let currentQuantity = this.env.pos.get_order().get_selected_orderline().get_quantity();

                    if(selectedLine.noDecrease) {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Invalid action'),
                            body: this.env._t('You are not allowed to change this quantity'),
                        });
                        return;
                    }
                    const parsedInput = event.detail.buffer && parse.float(event.detail.buffer) || 0;
                    if(lastId != selectedLine.cid)
                        this._showDecreaseQuantityPopup();
                    else if(currentQuantity < parsedInput)
                        this._setValue(event.detail.buffer);
                    else if(parsedInput < currentQuantity)
                        this._showDecreaseQuantityPopup();
                } else {
                    let { buffer } = event.detail;
                    let val = buffer === null ? 'remove' : buffer;
                    if (val !== 'remove' && val !== ''){
                        let order = this.env.pos.get_order();
                        let line = order.get_selected_orderline();
                        if (line){
                            let product_tmpl_id = line.product.product_tmpl_id
                            if (!await this.validateOrderQuantities(0, val, product_tmpl_id)){
                                NumberBuffer.reset();
                                return false;
                            }
                        }
                    }
                    this._setValue(val);
                }
            }
            async validateOrderQuantities(subtract=0, buffer=0, product_tmpl_id=null) {
                // Order quantities validation
                const order_lines = this.env.pos.get_order().get_orderlines()
                const products = order_lines.map(({quantity, product}) => [quantity, product.product_tmpl_id])
                const validate_category_quantities = await this.rpc({
                    model: 'res.partner',
                    method: 'validate_category_quantities',
                    args: [this.currentOrder.get_client(), products, subtract, buffer, product_tmpl_id],
                    kwargs: {},
                })

                if (validate_category_quantities) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Error en la validación de cantidades'),
                        body: this.env._t(validate_category_quantities),
                    });
                    return false;
                }
                else{
                    return true
                }
            }
        };

    Registries.Component.extend(ProductScreen, CCUProductScreen);

    return ProductScreen;
});
