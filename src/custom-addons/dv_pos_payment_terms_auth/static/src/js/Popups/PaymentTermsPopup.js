odoo.define('dv_pos_payment_terms_auth.PaymentTermsPopup', function (require) {
    'use strict';

    const { useState } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { useAutoFocusToLast } = require('point_of_sale.custom_hooks');

    class PaymentTermsPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this._id = 0;
            this.state = useState({ array: this._initialize(this.props.array) });
            useAutoFocusToLast();
        }

        _nextId() {
            return this._id++;
        }
        _emptyItem() {
            return {
                text: '',
                _id: this._nextId(),
            };
        }
        _initialize(array) {
            // If no array is provided, we initialize with one empty item.
            if (array.length === 0) return [this._emptyItem()];
            // Put _id for each item. It will serve as unique identifier of each item.
            return array.map((item) => Object.assign({}, { _id: this._nextId() }, typeof item === 'object' ? item : { 'text': item }));
        }
        removeItem(event) {
            const itemToRemove = event.detail;
            this.state.array.splice(
                this.state.array.findIndex(item => item._id == itemToRemove._id),
                1
            );
            // We keep a minimum of one empty item in the popup.
            if (this.state.array.length === 0) {
                this.state.array.push(this._emptyItem());
            }
        }
        createNewItem() {
            if (this.props.isSingleItem) return;
            this.state.array.push(this._emptyItem());
        }

        getPayload() {
            return {
                newArray: this.state.array
                    .map((item) => Object.assign({}, item)),
            };
        }
        selectionToInput(event) {
            if (event.target.value) {
                var selection = event.target.value;
                this.state.array[0].text = selection;
            }
        }
    }

    PaymentTermsPopup.template = 'PaymentTermsPopup';
    PaymentTermsPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        array: [],
        isSingleItem: false,
    };

    Registries.Component.add(PaymentTermsPopup);

    return PaymentTermsPopup;
});
