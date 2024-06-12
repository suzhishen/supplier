/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
const {Component, useState, onMounted} = owl;
import Dialog from 'web.Dialog';
import { qweb } from "web.core";

export class BlankUPC extends Component {
    setup() {
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        this.actionService = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            'print_label_type': 'normal',
            'printCount':1,
            'data':{
                'style':'',
                'color':'',
                'size':'',
            }
        })
        onMounted(()=>{
            this.initPrint()
        })
    }
    initPrint() {
        BrowserPrint.getDefaultDevice("printer", (device) => {
            this.selected_device = device;
        }, () => {
            alert('初始化失败')
        })
    }

    customAlert(title, content, type){
        this.notification.add(content, {
            title: title,
            type: type
        })
    }

    _checkData(data){
        let flag = true
        let msg = ''
        if(!data.style){
            this.customAlert('空白版款号必填！', '提醒', 'danger')
            flag = false
        }
        if(!data.color){
            this.customAlert('颜色必填！', '提醒', 'danger')
            flag = false
        }
        if(!data.size){
            this.customAlert('尺码必填！', '提醒', 'danger')
            flag = false
        }
        return flag
    }

    async onDirectPrint(){
        const data = this.state.data
        const flag = this._checkData(data)
        if(flag){
            let upc_data = await this.orm.call('blank.print.upc', 'blank_zpl_print_datas', [[0]], {
                data: this.state.data,
                type: this.state.print_label_type,
                qty: this.state.printCount
            })
            if(!upc_data){
                this.notification.add('未查询到UPC信息！', {
                    title: "提醒",
                    type: 'danger'
                })
            }
            else{
                this.selected_device.send(upc_data, (success)=>{
                    // this.actionService.doAction({ type: "ir.actions.act_window_close" })
                }, (error) => {
                    alert(`打印出错：${error}`)
                    this.selected_device = null;
                })
            }
        }

    }
}

BlankUPC.template = "fast_upc.blank_upc";


registry.category("actions").add("blank_print_upc", BlankUPC);
