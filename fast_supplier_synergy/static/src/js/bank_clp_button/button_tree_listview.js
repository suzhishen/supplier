/** @odoo-module **/

import {registry} from "@web/core/registry";
import {listView} from "@web/views/list/list_view";
import {ListRenderer} from "@web/views/list/list_renderer";
import {ListController} from "@web/views/list/list_controller";
import {useService} from "@web/core/utils/hooks";


export class BlankClpButtonListRenderer extends ListRenderer {
}

export class BlankClpButton extends ListController {
    setup() {
        this.action = useService('action')
        this.ormService = useService("orm");
        super.setup();
    }

    async synch_packing_list() {
        const records = this.model.root.selection;
        const recordIds = records.map((a) => a.resId);
        console.log(recordIds);
        await this.ormService.call('fast.blank.packing_list', 'btn_synch_packing_list', [recordIds])
    }
}

BlankClpButtonListRenderer.template = 'fastSupplierSynergy.BlankClpButtonTestListtView';
BlankClpButtonListRenderer.components = Object.assign({}, ListRenderer.components, {})

export const BlankClpButtonListListtView = {
    ...listView,
    Renderer: BlankClpButtonListRenderer,
    Controller: BlankClpButton,
    buttonTemplate: "BlankClpButtonTemplates",
};

registry.category("views").add("blank_clp_button_list", BlankClpButtonListListtView);
