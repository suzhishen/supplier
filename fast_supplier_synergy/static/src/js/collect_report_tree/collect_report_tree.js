/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import Dialog from 'web.Dialog';
import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";

export class ReportTest extends Component {
    setup() {
        this.orm = useService("orm");
        this.rpc = useService('rpc');
        this.notification = useService("notification");
        this.actionService = useService("action");
        this.dialog = useService('dialog');

        this.state = useState({
            lineDatas: [],
        });

        onMounted(() => {
            this.LoadDatas();
        });

        onWillUnmount(() => {
        });
    }

    async LoadDatas() {
        try {
            const response = await this.orm.call(
                'fast.blank.packing_list_detail',
                'collect_packing_list_difference',
                []
            );
            this.state.lineDatas = response.lines;
        } catch (error) {
            console.error('Failed to load lines:', error);
        }
    }

}

ReportTest.template = "fast_supplier_synergy.ReportTest";
registry.category("actions").add("report_test", ReportTest);
