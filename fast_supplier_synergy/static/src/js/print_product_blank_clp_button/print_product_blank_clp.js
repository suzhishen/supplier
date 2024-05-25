/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
const {Component, EventBus, onWillStart, useSubEnv, useState, onMounted, onWillDestroy, onWillUnmount} = owl;

export class PrintProductBlankClp extends Component {
    setup() {
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        this.actionService = useService("action");
        this.notification = useService("notification");
        this.state = useState({

        })
        this.active_ids = this.props.action.context.active_ids || []
        this.res_model = this.props.action.context.active_model || ''
        onWillStart(async () => {

        });

        onMounted(()=>{
            this.initZPLPrint()
            // this.onPrintTestUPC()
        })
    }

    initZPLPrint() {
        BrowserPrint.getDefaultDevice("printer", (device) => {
            this.selected_device = device;
        }, () => {
            alert('初始化失败')
        })
    }

    async onPrintUPC() {
        if(this.active_ids.length > 0){
            let result = await this.orm.call(this.res_model, 'get_clp_label_zpl_data', [this.active_ids])
            this.selected_device.send(result, undefined, (error) => {
                alert(`打印出错：${error}`)
            })
        }
        this.closeDialog()
    }
    closeDialog(){
        this.actionService.doAction({
            type: "ir.actions.act_window_close",
        });
    }
    onPrintTestUPC(){
        let zpl = `
^XA
~TA000
~JSN
^LT0
^MNW
^MTD
^PON
^PMN
^LH0,0
^JMA
^PR6,6
~SD15
^JUS
^LRN
^CI28
^PA0,1,1,0
^XZ
            
^XA
^MMT
^PW599
^LL400
^LS0
^FO214,8^A@N,35,35,E:SIMSUN.FNT^FD乐达面料仓^FS
^FO2,46^GB597,0,1^FS
^FB300,2,0,L,0
^FO9,59^A@N,30,30,E:SIMSUN.FNT^FD供应商:测试^FS
^FB300,2,0,L,0
^FO9,137^A@N,30,30,E:SIMSUN.FNT^FD编码:测试^FS
^FB300,2,0,L,0
^FO9,307^A@N,30,30,E:SIMSUN.FNT^FD品名:测试^FS
^FB300,2,0,L,0
^FO9,213^A@N,30,30,E:SIMSUN.FNT^FD缸号-匹号:66666-6^FS
^FT328,380^BQN,2,10
^BY12
^FH\^FD>:66666-6^FS
^XZ`
        if(!this.selected_device || this.selected_device == undefined){
                alert('打印机初始化失败！')
        }
        else{
            this.selected_device.send(zpl, undefined, (error) => {
                alert(`打印出错：${error}`)
            })
        }
        this.closeDialog()
    }

    //---- Data ----
}

PrintProductBlankClp.template = "print_product_blank_clp";


registry.category("actions").add("PrintProductBlankClp", PrintProductBlankClp);
