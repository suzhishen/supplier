/** @odoo-module **/

import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";
import {patch} from "@web/core/utils/patch";

patch(SelectCreateDialog.prototype, "fast_SelectCreateDialog_searchpanel", {
    setup() {
        this._super(...arguments);
        const context = this.props.context || {}
        if(context && context.showSearchPannel){
            this.baseViewProps.display = {
                searchPanel: true
            }
        }
    }
});