odoo.define('ccu_pos.ActionpadWidgetValidate', function (require) {
    "use strict";

    const { useListener } = require('web.custom_hooks');
    const ActionpadWidget = require('point_of_sale.ActionpadWidget');
    const Registries = require('point_of_sale.Registries');

    const ActionpadWidgetValidate = ActionpadWidget =>
        class extends ActionpadWidget {
            constructor() {
                super(...arguments);
                useListener('click-pay-validate', this.clickPayValidate);
                this.clienteGenerico();
            }
            clienteGenerico(){
                if(this.currentOrder != null){
                    let part = this.env.partners;
                    let cust = null;
                    for(var i = 0; i < part.length; i++){
                        if(part[i].name === 'Cliente Boleta'){
                            cust = part[i];
                        }
                    }
                    this.currentOrder.set_client(cust);
                }
            }
            clickPayValidate(){
                if(this.props.partner === null){
                    console.log("clickPayValidate - partner");
                    this.showPopup('ErrorPopup', {
                        title: "Error",
                        body: "Seleccione un Cliente para continuar la venta",
                    });
                }else if(this.env.pos.products.length === 0){
                    console.log("clickPayValidate - partner");
                    this.showPopup('ErrorPopup', {
                        title: "Error",
                        body: "Seleccione un Producto como mínimo para continuar la venta",
                    });
                }else{
                    console.log("clickPayValidate - listo");
                }

            }
        }

    Registries.Component.extend(ActionpadWidget, ActionpadWidgetValidate);

    return ActionpadWidget;

});
