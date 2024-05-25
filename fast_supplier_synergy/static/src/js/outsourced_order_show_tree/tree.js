/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useBus, useService} from "@web/core/utils/hooks";

const {Component, onWillStart, useState, onWillUpdateProps, useEffect} = owl;
import {ConfirmationDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import Dialog from 'web.Dialog';

export class FastOutsourcedOrderShowTree extends Component {
    setup() {
        this.ormService = useService("orm");
        this.actionService = useService("action");
        this.notification = useService('notification');
        this.dialog = useService('dialog');
        this.state = useState({
            orderRecord: {
                'datas': []
            },
            apply_order_line_ids: [],
            chargeback_blank_order_datas: []
        })

        onWillStart(async () => {
            this.state.orderRecord = await this.ormService.call(this.props.record.resModel, 'get_outsourced_order_show_datas', [[this.props.record.resId]])
        })

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.record.resId !== this.props.record.resId && nextProps.record.resId === false) {
                this.state.orderRecord = {
                    datas: []
                }
            }
            if ((nextProps.record.resId !== this.props.record.resId && nextProps.record.resId > 0) || nextProps.readonly === true) {
                this.state.orderRecord = await this.ormService.call(this.props.record.resModel, 'get_outsourced_order_show_datas', [[nextProps.record.resId]])
            }
        })
    }

    _unlinkOutsourcedApplyOrderLineIds(unlink_ids) {
        unlink_ids.forEach(line_id => {
            let exist_index = this.state.apply_order_line_ids.findIndex(l_id => l_id === line_id)
            if (exist_index > -1) {
                this.state.apply_order_line_ids.splice(exist_index, 1)
            }
        })
    }

    _addOutsourcedApplyOrderLineIds(add_ids) {
        add_ids.forEach(add_id => {
            let exist_index = this.state.apply_order_line_ids.findIndex(a_id => a_id === add_id)
            if (exist_index <= -1) {
                this.state.apply_order_line_ids.push(add_id)
            }
        })
    }

    _unlinkProductChargebackBlankOrderDatas(delete_id, key) {
        const chargeback_blank_order_datas = this.state.chargeback_blank_order_datas.filter(item => !(item[key] === delete_id));
        this.state.chargeback_blank_order_datas = chargeback_blank_order_datas
    }

    _addProductChargebackBlankOrderDatas(productDatas) {
        productDatas.forEach(data => {
            if (data.product_qty === 0) {
                this._unlinkProductChargebackBlankOrderDatas(data.product_id, 'product_id')
            } else {
                const existingIndex = this.state.chargeback_blank_order_datas.findIndex(item =>
                    item.product_id === data.product_id && item.product_tmpl_id === data.product_tmpl_id
                );
                if (existingIndex !== -1) {
                    this.state.chargeback_blank_order_datas[existingIndex] = data;
                } else {
                    this.state.chargeback_blank_order_datas.push(data);
                }
            }
        });
    }

    async applyOutsourcedMaterialRequisitionBtn() {
        let result = await this.ormService.call(this.props.record.resModel, 'action_apply_material_requisition', [[this.props.record.resId]], {apply_order_line_ids: this.state.apply_order_line_ids})
        this.actionService.doAction(result);
    }

    async chargebackBlankOrderBtn() {
        this.dialog.add(ConfirmationDialog, {
            title: "退单提示",
            body: "确认将选择的数量退回到待分配吗？",
            confirm: async () => {
                let result = await this.ormService.call(this.props.record.resModel, 'btn_chargeback_blank_order_to_allocate', [[this.props.record.resId]], {
                    chargeback_blank_order_datas: this.state.chargeback_blank_order_datas
                })
                this.state.chargeback_blank_order_datas = []
                this.state.apply_order_line_ids = []
                await this.props.record.model.load({'resId': this.props.record.resId});
                await this.props.record.model.notify()
            },
            cancel: () => {
            },
        });
    }

    async update_date(event){
        // 更新预计交期
        this.ormService.call('fast.blank_order_detail', 'update_date_expected', [[]], {
            'product_color_name': event.target.className,
            'date_expected': event.target.value,
        })
        console.log(event)
        console.log(event.target.className)
        console.log(event.target.value)
    }
}

FastOutsourcedOrderShowTree.template = 'fast_supplier_synergy.outsourced_order_show_tree'
registry.category("view_widgets").add("fast_order_center_outsourced_order_show_tree", FastOutsourcedOrderShowTree);