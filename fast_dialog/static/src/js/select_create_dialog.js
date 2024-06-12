/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";
import { Dialog } from "@web/core/dialog/dialog";


Dialog.props.size = { type: String, optional: true}

const LEGACY_SIZE_CLASSES = {
    "extra-large": "modal-xl",
    large: "modal-lg",
    small: "modal-sm",
};

const FAST_SIZE_CLASSES = {
    "extra-modal-max-80": "extra-modal-max-80",
    "extra-modal-max-85": "extra-modal-max-85",
    "extra-modal-max-90": "extra-modal-max-90",
    "extra-modal-max-95": "extra-modal-max-95",
};

patch(SelectCreateDialog.prototype, 'fast_SelectCreateDialog_new', {

    setup() {
        this._super();
        const context = this.props && this.props.context;
        const actionDialogSize = context && context.dialog_size;
        this.size = 'lg'
        if(actionDialogSize){
            this.size = FAST_SIZE_CLASSES[actionDialogSize] || LEGACY_SIZE_CLASSES[actionDialogSize] || 'lg';
        }
    }

});
