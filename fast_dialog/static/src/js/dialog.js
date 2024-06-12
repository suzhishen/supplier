/** @odoo-module **/

import { ActionDialog } from '@web/webclient/actions/action_dialog';
import { Dialog } from '@web/core/dialog/dialog';
import { patch } from "@web/core/utils/patch";
import { useHotkey } from "@web/core/hotkeys/hotkey_hook";

const LEGACY_SIZE_CLASSES = {
    "extra-large": "modal-xl",
    large: "modal-lg",
    small: "modal-sm",
};

const FAST_SIZE_CLASSES = {
    "extra-modal-max-55": "extra-modal-max-55",
    "extra-modal-max-60": "extra-modal-max-60",
    "extra-modal-max-65": "extra-modal-max-65",
    "extra-modal-max-70": "extra-modal-max-70",
    "extra-modal-max-75": "extra-modal-max-75",
    "extra-modal-max-80": "extra-modal-max-80",
    "extra-modal-max-85": "extra-modal-max-85",
    "extra-modal-max-90": "extra-modal-max-90",
    "extra-modal-max-95": "extra-modal-max-95",
};

patch(ActionDialog.prototype, 'fast_dialog', {

    setup() {
        this._super();
        this.close_footer = false;
        const actionProps = this.props && this.props.actionProps;
        const actionContext = actionProps && actionProps.context;
        const actionDialogSize = actionContext && actionContext.dialog_size;
        if(actionContext && actionContext.dialog_size){
            this.props.size = FAST_SIZE_CLASSES[actionDialogSize] || LEGACY_SIZE_CLASSES[actionDialogSize] || ActionDialog.defaultProps.size;
        }
        if(actionProps && actionProps.action && actionProps.action.context && actionProps.action.context.close_footer){
            this.close_footer = true
        }
    }

});

// patch(Dialog.prototype, 'fast.dialog', {
//
//     setup() {
//         this._super();
//         useHotkey("escape", () => {
//             this.close();
//         });
//     },
//
//     async close(){
//         this.data.close();
//         debugger
//         // 当存在force_refresh=='refresh'，关闭弹窗时强制刷新
//         // if(this.record && this.record.model  && this.record.context && this.record.context.force_refresh === 'refresh'){
//         //     await this.record.model.load();
//         //     this.record.model.notify();
//         // }
//     }
//
// });