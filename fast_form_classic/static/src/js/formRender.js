/** @odoo-module **/
import {patch} from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { FormRenderer } from "@web/views/form/form_renderer";
import { browser } from "@web/core/browser/browser";
import {
    onMounted,
} from "@odoo/owl";

patch(FormRenderer.prototype, 'fast.FormRenderer', {
    setup() {
        this._super.apply()
        onMounted(() => {
            browser.addEventListener("resize", this.onResize)
            const header = document.querySelector('.statusbar-wrapper')
            let sheet = document.querySelector('.o_form_sheet')
            if(header && sheet){
                const header_height = header.offsetHeight
                if(header_height > 0){
                    sheet.style.marginTop = header_height + 5 + 'px'
                }
            }
        });
    }
})