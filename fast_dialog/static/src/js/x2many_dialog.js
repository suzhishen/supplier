/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { X2ManyFieldDialog } from "@web/views/fields/relational_utils";
import { useService } from "@web/core/utils/hooks";

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

patch(X2ManyFieldDialog.prototype, 'fast_X2ManyFieldDialog', {

    setup() {
        this._super();
        this.actionService = useService("action");
        const context = this.props && this.props.record && this.props.record.context;
        const actionDialogSize = context && context.dialog_size;
        this.size = 'lg'
        if(actionDialogSize){
            this.size = FAST_SIZE_CLASSES[actionDialogSize] || LEGACY_SIZE_CLASSES[actionDialogSize] || 'lg';
        }
    },

    async close(){
        if(this.record && this.record.model  && this.record.context && this.record.context.default_parent_res_id
            && this.record.context.force_refresh === 'refresh'){
            await this.record.model.load({'resId': this.record.context.default_parent_res_id});
            this.record.model.notify();
        }
        this.props.close()
    }

});
