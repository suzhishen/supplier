/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
const {Component, useState, onMounted} = owl;
import Dialog from 'web.Dialog';
import { qweb } from "web.core";

export class BlankUPCView extends Component {
    setup() {
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        this.actionService = useService("action");
        this.notification = useService("notification");

    }

    async click1(){
        let result = await this.orm.call('blank.print.upc', 'open_blank_upc_action', [[0]], {})
        this.actionService.doAction(result)
    }

    async click2(){
        let result = await this.orm.call('blank.print.upc', 'open_blank_upc_action2', [[0]], {})
        this.actionService.doAction(result)
    }

}

BlankUPCView.template = "fast_upc.blank_upc_view";


registry.category("actions").add("blank_upc_view", BlankUPCView);
