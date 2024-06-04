/** @odoo-module **/

import {
    Component,
    onWillStart,
    useSubEnv,
    useEffect,
    useRef,
    onWillUnmount,
    onWillUpdateProps,
    useState
} from "@odoo/owl";
import {useService,} from "@web/core/utils/hooks";
import {ConfirmationDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import Dialog from 'web.Dialog';
import {qweb} from "web.core";


export class PackingTreeRender extends Component {
    setup() {
        this.ormService = useService("orm");
        this.actionService = useService("action");
        this.notification = useService('notification');
        this.rpcService = useService("rpc");
        this.dialog = useService('dialog');
        this.rpc = useService('rpc');
    }

    initZPLPrint(datas, quantitys_list, updateData, records_ids) {
        BrowserPrint.getDefaultDevice("printer", (device) => {
            this.selected_device = device;
            this.onPrintUPC(datas, quantitys_list, updateData, records_ids)
        }, () => {
            alert('初始化失败')
        })
    }

    async onPrintUPC(datas, quantitys_list, updateData, records_ids) {
        let result = await this.ormService.call('fast.blank.packing_list_detail', 'get_save_clp_label_zpl_data', [[]], {
            datas: datas,
            quantitys_list: quantitys_list,
            updateData_list: updateData,
            records_ids: records_ids,
        })
        this.selected_device.send(result, undefined, (error) => {
            alert(`打印出错：${error}`)
        })
        this.closeDialog()
    }

    closeDialog() {
        this.actionService.doAction({
            type: "ir.actions.act_window_close",
        });
    }

    async editStyleInfo(event, data) {
        console.log(event)
        event.target.disabled = true;
        setTimeout((button)=>{event.target.disabled = false}, 500)  // 防止多次点击按钮
        console.log(data)
        let self = this
        self.ormService.call('fast.blank.packing_list_detail', 'get_packed_list_datas', [], {
            'po': data.po,
            'product_code': data.product_tmpl_code
        }).then(result => {
            let incompleteLineJson = JSON.stringify(data.incomplete_line);
            let incompleteLineEncoded = encodeURIComponent(incompleteLineJson);
            let packedListJson = JSON.stringify(result.data);
            let packedListEncoded = encodeURIComponent(packedListJson);
            let packedSizeJson = JSON.stringify(result.existing_data);
            let packedSizeEncoded = encodeURIComponent(packedSizeJson);
            let mixedStowageJson = JSON.stringify(result.mixed_stowage_sequence_value);
            let mixedStowageEncoded = encodeURIComponent(mixedStowageJson);
            let packing_detail_follow_val_json = JSON.stringify(result.packing_detail_follow_val);
            let packing_detail_follow_val_encoded = encodeURIComponent(packing_detail_follow_val_json);
            let packing_follow_config_val_json = JSON.stringify(result.packing_follow_config_val);
            let packing_follow_config_val_encoded = encodeURIComponent(packing_follow_config_val_json);
            let order_packing_win = layui.layer.open({
                title: data.po + ' / ' + data.product_tmpl_code,
                type: 2,
                area: ['80%', '85%'],
                // content: `fast_supplier_synergy/static/src/js/packing_tree/packing_add_data_render_view.html?incomplete_line=${incompleteLineEncoded}&packed_list=${packedListEncoded}`,
                content: `fast_supplier_synergy/static/src/js/packing_tree/packing_add_data_render_view.html?incomplete_line=${incompleteLineEncoded}&packed_list=${packedListEncoded}&packed_size=${packedSizeEncoded}&mixed_stowage_sequence_value=${mixedStowageEncoded}&packing_detail_follow_val=${packing_detail_follow_val_encoded}&packing_follow_config_val=${packing_follow_config_val_encoded}`,
                fixed: false, // 不固定
                maxmin: true,
                shadeClose: false,
                btn: ['保存并打印', '取消'],
                btnAlign: 'c',
                yes: async function (index, layero) {
                    console.log('获取 iframe 中的输入框标记值');
                    let title = layero[0].firstChild.innerText
                    // 获取 iframe 的窗口对象
                    var iframeWin = window[layero.find('iframe')[0]['name']];
                    var deleteData = $(iframeWin.document).find('#deleteID')[0].value // 获取删除记录id

                    // {s:[['3','4'], ['3','4']], m[['4','3']], ['4','3']}
                    var qs_tr = $(iframeWin.document).find('#formData .accordion-body tbody tr')
                    var updateData = {};
                    var formData = {};
                    for (var i = 0; i < qs_tr.length; i++) {
                        if(qs_tr[i].id){
                            updateData[qs_tr[i].id] = []
                        }else{
                            var size_name = qs_tr[i].className
                            formData[size_name] = []
                        }
                    }
                    for (var i = 0; i < qs_tr.length; i++) {
                        if(qs_tr[i].id){
                            var input0 = qs_tr.eq(i).find('input')[0].value
                            var input1 = qs_tr.eq(i).find('input')[1].value
                            updateData[qs_tr[i].id].unshift([input0, input1])
                        }else {
                            var size_name = qs_tr[i].className
                            var input0 = qs_tr.eq(i).find('input')[0].value
                            var input1 = qs_tr.eq(i).find('input')[1].value
                            formData[size_name].unshift([input0, input1])
                        }
                    }
                    console.log(formData)

                    // {s:['3','4'], m['4','3']}
                    var hz_inputs = iframeWin.document.getElementById('hzBox').getElementsByTagName('input');
                    var hz_updateData = {};
                    var hz_formData = {};
                    for (var i = 0; i < hz_inputs.length; i++) {
                        var input = hz_inputs[i];
                        if (input.name) {
                            if (hz_formData[input.name]) {
                                if (input.id) {
                                    hz_updateData[input.id] = input.value;
                                } else {
                                    hz_formData[input.name].push(input.value);
                                }
                            } else {
                                if (input.id) {
                                    hz_updateData[input.id] = input.value;
                                } else {
                                    hz_formData[input.name] = [input.value];
                                }
                            }
                        }
                    }

                    // [{s:'3', m:'4'}, {s:'4', m:'3'}]
                    var hz_box_input = iframeWin.document.querySelectorAll('.hz_box');
                    console.log(hz_box_input)
                    var hz_box_createData_list = []
                    var hz_box_updateData_list = []
                    for (var i = 0; i < hz_box_input.length; i++) {
                        var hz_box_createData = {};
                        var hz_box_updateData = {};
                        var hz_input_ele = hz_box_input[i].getElementsByTagName('input')
                        for (var j = 0; j < hz_input_ele.length; j++) {
                            var input = hz_input_ele[j];
                            if (input.name) {
                                hz_box_createData[input.name] = input.value;
                            }
                            if (input.id) {
                                hz_box_updateData[input.id] = input.value;
                            }
                        }
                        hz_box_createData_list.push(hz_box_createData)
                        hz_box_updateData_list.push(hz_box_updateData)
                    }

                    console.log(title);
                    console.log(formData);
                    console.log(hz_formData);
                    console.log(hz_box_createData_list);
                    console.log(hz_updateData);
                    // console.log("S: " + formData["S"]);
                    // console.log("M: " + formData["M"]);
                    self.createDetail(data, formData, updateData, deleteData, hz_box_createData_list, hz_box_updateData_list)
                    layer.close(order_packing_win);
                },
            });
        });
    }

    confirmCallback() {
        console.log('确认执行操作')
    }

    async createDetail(datas, quantitys_list, updateData, deleteData, hz_box_createData_list, hz_box_updateData_list) {
        let self = this
        // await this.ormService.call('fast.blank.packing_list', 'create_blanK_packing_list', [[]], {
        await this.ormService.call('fast.blank.packing_list', 'create_packing_detail_follow', [[]], {
            datas: datas,
            quantitys_list: quantitys_list,
            updateData: updateData,
            deleteData: deleteData,
            hz_box_createDate_list: hz_box_createData_list,
            hz_box_updateData_list: hz_box_updateData_list,
        }).then(result => {
            console.log(result)
            if (result) {
                layui.layer.msg('更新成功');
                self.ormService.call('fast.blank.packing_list_detail', 'get_packed_list_datas', [], {
                    'po': datas.po,
                    'product_code': datas.product_tmpl_code
                }).then(next_result => {
                    console.log(next_result)
                    // 更新前端数据
                    next_result.data.forEach(record => {
                        $(`.${datas.product_tmpl_code}-${record.size}`).html(record.quantity)
                    })
                    // 未检测到数据更新则重置
                    if (!next_result.data.length){
                        datas.incomplete_line.forEach(record => {
                            $(`.${datas.product_tmpl_code}-${record.size_name}`).html(0)
                        })
                    }
                })
                self.initZPLPrint(datas, quantitys_list, updateData, result.records_ids)

            } else {
                layui.layer.msg('更新失败, 请联系管理员', {
                    time: 600000, // 600s后自动关闭
                    btn: ['我已知晓']
                });
            }
        });
    }

    async onchangeDataStype(event) {
        console.log(event)
        const input = event.target.value;
        if (!/^[0-9]*$/.test(input)) {
            this.input_invalid = true;
            event.target.classList.add('invalid');
        } else {
            this.input_invalid = false;
            event.target.classList.remove('invalid');
        }
    }

    async viewBlankIncomingDetail(data) {
        let product_tmpl_id = data.product_tmpl_id;
        let outsource_order_blank_id = data.order_id;
        let result = await this.ormService.call(this.props.resModel, 'btn_open_fast_stock_move_line_blank_action', [[]], {
            product_tmpl_id: product_tmpl_id,
            outsource_order_blank_id: outsource_order_blank_id
        })
        this.actionService.doAction(result);
    }

    async actionReviewBlankIn(data) {
        let result = await this.ormService.call(this.props.resModel, 'action_open_fast_order_center_packing_tree_blank_in_client', [[]], {
            po_style_data: data
        })
        this.actionService.doAction(result);
    }

    async viewStyleMaterialDetailInfo(data) {
        let result = await this.ormService.call(this.props.resModel, 'btn_view_outsource_blank_order_line_material_detail', [[]], {
            line_ids: data.line_ids
        })
        this.actionService.doAction(result);
    }

    async update_date(e, data) {
        console.log(e)
        console.log(data.product_tmpl_code)
        console.log(e.target.value)
        // 更新预计交期
        this.ormService.call('fast.blank_order_detail', 'update_date_expected', [[]], {
            'po': data.po,
            'product_color_name': data.product_tmpl_code,
            'date_expected': e.target.value,
        })
    }

    async onlyConfirmStyleColorMaterialRequirementsClick(data) {
        let action = await this.ormService.call(this.props.resModel, 'get_blank_order_bom_detail', [[]], data)
        this.actionService.doAction(action)
    }
}

PackingTreeRender.template = 'fast_supplier_synergy.PackingTreeRenderView'

PackingTreeRender.props = [
    'resModel',
    'model',
    'standProps',
]


