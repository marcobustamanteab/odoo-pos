odoo.define('ccu_pos_note.ButtonOrderNote', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class ButtonOrderNote extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        get selectedOrder() {
            return this.env.pos.get_order();
        }
        async onClick() {
            console.log("onClick")
            if (!this.selectedOrder) return;

            const { confirmed, payload: inputNote } = await this.showPopup('TextAreaPopup', {
                startingValue: this.selectedOrder.get_note(),
                title: this.env._t('Nota'),
            });

            if (confirmed) {
                this.selectedOrder.set_note(inputNote);
            }
        }
    }
    ButtonOrderNote.template = 'ButtonOrderNote';

    ProductScreen.addControlButton({
        component: ButtonOrderNote,
        condition: function() {
            return this.env.pos.config.order_note;
        },
    });

    Registries.Component.add(ButtonOrderNote);

    return ButtonOrderNote;
});
