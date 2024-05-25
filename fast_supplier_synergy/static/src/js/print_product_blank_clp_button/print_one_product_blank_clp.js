/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const {Component, EventBus, onWillStart, useSubEnv, useState, onMounted, onWillDestroy, onWillUnmount, xml} = owl;
import Dialog from 'web.Dialog';

export class PrintOneProductBlankClp extends Component {
    setup() {
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        this.actionService = useService("action");
        this.notification = useService("notification");
        this.state = useState({})
        this.active_ids = this.props.action.context.active_ids || []
        this.res_model = this.props.action.context.active_model || ''
        onWillStart(async () => {
        });

        onMounted(() => {
            this.initZPLPrint()
            // this.onPrintTestUPC()
        })
    }

    initZPLPrint() {
        BrowserPrint.getDefaultDevice("printer", (device) => {
            this.selected_device = device;
            this.onPrintUPC()
            setTimeout(function () {
                $('.btn-close').click()
            }, 500);
        }, () => {
            alert('初始化失败')
        })
    }

    async onPrintUPC() {
        if (this.active_ids.length > 0) {
            let result = await this.orm.call(this.res_model, 'get_one_clp_label_zpl_data', [this.active_ids])
            this.selected_device.send(result, undefined, (error) => {
                alert(`打印出错：${error}`)
            })
        }
        this.closeDialog()
    }

    closeDialog() {
        this.actionService.doAction({
            type: "ir.actions.act_window_close",
        });
    }
    //---- Data ----
}

PrintOneProductBlankClp.template = xml`<div style="text-align: center;padding: 10px;font-size: 20px;">打印中...</div>`;


registry.category("actions").add("PrintOneProductBlankClp", PrintOneProductBlankClp);
