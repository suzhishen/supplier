/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useBus, useService} from "@web/core/utils/hooks";

const {Component, onWillStart, useState, onWillUpdateProps, useEffect, onMounted} = owl;
import {ConfirmationDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import Dialog from 'web.Dialog';

export class CustomWidget extends Component {
    setup() {
        this.ormService = useService("orm");
        this.actionService = useService("action");
        this.notification = useService('notification');
        this.dialogService = useService('dialog');

        onMounted(()=>{
            this.initPrint()
        })
    }

    async btnClick(){
        await this.props.record.save();
        let upc_data = await this.ormService.call(this.props.record.resModel, 'trigger_widget_click', [this.props.record.resId], {})
        if(!upc_data){
            this.notification.add('未查询到UPC信息！', {
                title: "提醒",
                type: 'danger'
            })
        }
        else{
            this.selected_device.send(upc_data, (success)=>{
                this.props.record.update({
                    product_id:false
                })
                // this.actionService.doAction({ type: "ir.actions.act_window_close" })
            }, (error) => {
                alert(`打印出错：${error}`)
                this.selected_device = null;
            })
        }
    }

    initPrint() {
        BrowserPrint.getDefaultDevice("printer", (device) => {
            this.selected_device = device;
        }, () => {
            alert('初始化失败')
        })
    }
}

CustomWidget.template = 'fast_upc.custom_widget'
registry.category("view_widgets").add("custom_widget", CustomWidget);
