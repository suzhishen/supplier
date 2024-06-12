/** @odoo-module **/
import {patch} from "@web/core/utils/patch";
import {ViewButton} from "@web/views/view_button/view_button";
import {evaluateExpr} from "@web/core/py_js/py";
import {pick} from "@web/core/utils/objects";
import { DROPDOWN } from "@web/core/dropdown/dropdown";

patch(ViewButton.prototype, 'fast.ViewButton', {
    onClick(ev) {
        let buttonContext = {};
        if (typeof this.clickParams.context === "string") {
            buttonContext = evaluateExpr(this.clickParams.context, this.getResParams.evalContext);
        } else {
            buttonContext = this.clickParams.context;
        }

        if (this.props.tag === "a") {
            ev.preventDefault();
        }

        if (this.props.onClick) {
            return this.props.onClick();
        }

        this.env.onClickViewButton({
            clickParams: this.clickParams,
            getResParams: () =>
                pick(this.props.record, "context", "evalContext", "resModel", "resId", "resIds"),
            beforeExecute: () => {
                if (buttonContext && buttonContext.button_switch_model && this.props && this.props.record) {
                    switch (buttonContext.button_switch_model) {
                        case('edit'):
                            return this.props.record.switchMode("edit");
                        case('readonly'):
                            return this.props.record.switchMode("readonly");
                    }
                }
                if (this.env[DROPDOWN]) {
                    this.env[DROPDOWN].close();
                }
            },
            disableAction: this.props.disable,
            enableAction: this.props.enable,
        });


    },

    get getResParams() {
        return pick(this.props.record, "context", "evalContext", "resModel", "resId", "resIds")
    }
})