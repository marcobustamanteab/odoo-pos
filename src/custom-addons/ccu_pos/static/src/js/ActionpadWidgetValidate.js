odoo.define('ccu_pos.ActionpadWidgetValidate', function (require) {
    "use strict";

    const { useListener } = require('web.custom_hooks');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class ActionpadWidgetValidate extends PosComponent {
            constructor() {
                super(...arguments);
                useListener('click-pay-validate', this.clickPayValidate);
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
    ActionpadWidgetValidate.template = 'ActionpadWidgetValidate';

    Registries.Component.add(ActionpadWidgetValidate);

    return ActionpadWidgetValidate;

});
