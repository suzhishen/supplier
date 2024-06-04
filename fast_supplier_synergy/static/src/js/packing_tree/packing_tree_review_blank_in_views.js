/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useBus, useService} from "@web/core/utils/hooks";

const {Component, onWillStart, useState, onWillUpdateProps, useEffect, onMounted} = owl;
import {ConfirmationDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import Dialog from 'web.Dialog';

export class fastOrderCenterPackingTreeBlankIn extends Component {
    setup() {
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        this.actionService = useService("action");
        this.notification = useService("notification");
        this.state = useState({})

        onWillStart(async () => {
            const record = this.props.action.context.record
            this.state.record = record && record !== 'undefined' ? record : {};
        })
    }

    async viewInMoveDatas(datas){
        const move_line_ids = datas.move_line_ids
        let result = await this.orm.call('fast.outsource.order.blank.line', 'btn_view_outsource_blank_move_datas_detail', [[]], {
            move_line_ids: move_line_ids,
            type: 'in'
        })
        this.actionService.doAction(result);
    }

    async viewOutMoveDatas(datas){
        const move_line_ids = datas.move_line_ids
        let result = await this.orm.call('fast.outsource.order.blank.line', 'btn_view_outsource_blank_move_datas_detail', [[]], {
            move_line_ids: move_line_ids,
            type: 'out'
        })
        this.actionService.doAction(result);
    }
}

fastOrderCenterPackingTreeBlankIn.template = "fastOrderCenter.packingTreeBlankIn";


registry.category("actions").add("fast_order_center_packing_tree_blank_in", fastOrderCenterPackingTreeBlankIn);