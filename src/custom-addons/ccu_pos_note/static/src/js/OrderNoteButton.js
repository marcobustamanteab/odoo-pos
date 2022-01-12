odoo.define('ccu_pos_note.OrderNoteButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class ButtonOrderlineNote extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        get selectedOrderline() {
            return this.env.pos.get_order().get_selected_orderline();
        }
        async onClick() {
            console.log("onClick")
            if (!this.selectedOrderline) return;

            const { confirmed, payload: inputNote } = await this.showPopup('TextAreaPopup', {
                startingValue: this.selectedOrderline.get_note(),
                title: this.env._t('Nota en Linea'),
            });

            if (confirmed) {
                this.selectedOrderline.set_note(inputNote);
            }
        }
    }
    ButtonOrderlineNote.template = 'ButtonOrderlineNote';

    ProductScreen.addControlButton({
        component: ButtonOrderlineNote,
        condition: function() {
            return this.env.pos.config.orderline_note;
        },
    });

    Registries.Component.add(ButtonOrderlineNote);

    return ButtonOrderlineNote;



    class ButtonOrderNote extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        get selectedOrderline() {
            return this.env.pos.get_order().get_selected_orderline();
        }
        async onClick() {
            console.log("onClick")
            if (!this.selectedOrderline) return;

            const { confirmed, payload: inputNote } = await this.showPopup('TextAreaPopup', {
                startingValue: this.selectedOrderline.get_note(),
                title: this.env._t('Nota'),
            });

            if (confirmed) {
                this.selectedOrderline.set_note(inputNote);
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
