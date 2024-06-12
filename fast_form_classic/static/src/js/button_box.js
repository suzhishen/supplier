/** @odoo-module **/
import {patch} from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ButtonBox } from "@web/views/form/button_box/button_box";

patch(ButtonBox.prototype, 'fast.ButtonBox', {
    setup() {
        this._super.apply();
        const ui = useService("ui");
        this.getMaxButtons = () => [2, 2, 2, 4][ui.size] || 9;
    }
})