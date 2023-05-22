odoo.define('ccu_post_consigment.custom_tree_button', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var CustomTreeButton = Widget.extend({
        template: 'ccu_post_consigment.custom_tree_button',

        events: {
            'click .custom-tree-button': '_onClick',
        },

        _onClick: function (ev) {
            ev.preventDefault();
            console.log('Button clicked!');
        },
    });

    core.action_registry.add('custom_tree_button', CustomTreeButton);

    return CustomTreeButton;
});
