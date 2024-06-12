/** @odoo-module **/
import {patch} from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { FormCompiler } from "@web/views/form/form_compiler";
import {
    append,
    combineAttributes,
    createElement,
    createTextNode,
    getTag,
} from "@web/core/utils/xml";

patch(FormCompiler.prototype, 'fast.FormCompiler', {
    compileHeader(el, params) {
        const statusBarWrapper = createElement("div");
        statusBarWrapper.className="statusbar-wrapper"
        const statusBar = this._super.apply(this, arguments)
        statusBar.className =
            "o_form_statusbar position-relative d-flex justify-content-between border-bottom-cus";
        append(statusBarWrapper, statusBar);
        return statusBarWrapper;
    }
})