/** @odoo-module */

import {Component, onWillUnmount, onMounted, onWillStart, onWillUpdateProps, useState, useEffect, xml} from "@odoo/owl";


export class report_tree_renderer extends Component {
    setup() {
        this.orm = this.props.list.model.orm
        this.sizeList = {}
        this.sizeS = []
        this.sizeT = []
        this.list = useState({
            records: this.props.list.records
        })
        this.difference_data = []
        onWillStart(async () => {
            const response = await this.orm.call('fast.blank.packing_list_detail', 'get_rep_size_list', [], {})
            this.sizeList = response.data
            const number = response.data.t.length - response.data.s.length
            if (number > 0) {
                this.sizeS = new Array(Math.abs(number)).fill('th');
            } else {
                this.sizeT = new Array(Math.abs(number)).fill('th');
            }

            const rest = await this.orm.call('fast.blank.packing_list_detail', 'packing_list_difference', [], {})
            let value = JSON.parse(rest)
            this.difference_data = value.data
            console.log(this.difference_data)
        })

        useEffect(() => {
            // 异步操作
            var ids = [];
            this.props.list.records.forEach((value) => {
                ids.push(value._values.id);
            });
            const fetchData = async () => {
                try {
                    console.log("Successful fetching records");
                    // const response = await this.orm.call('fast.blank.packing_list_detail', 'get_records_format_data', [ids], {});
                    // this.list.records = response;
                } catch (error) {
                    console.error("Error fetching records:", error);
                }
            };

            fetchData();

            // 返回清理函数
            return () => {
                // 清理操作（如果需要）
            };
        }, () => [this.props.list.records]);

    }

}


report_tree_renderer.template = `fast_supplier_synergy.report_tree_renderer`;


