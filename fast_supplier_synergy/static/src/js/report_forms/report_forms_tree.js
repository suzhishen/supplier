/** @odoo-module */

import {registry} from "@web/core/registry"
import {useService} from "@web/core/utils/hooks";

const {Component, whenReady, useRef, onRendered, onWillUpdateProps, onMounted, useState, onWillStart} = owl;

export class ReportFormsTree extends Component {
    setup() {
        this.orm = useService("orm");
        this.user = useService("user");
        this.rpc = useService("rpc")
        this.notification = useService("notification");
        this.action = useService("action");
        this.state = useState({
            selects: [],
        })
        this.sizeList = {}
        this.sizeS = []
        this.sizeT = []
        this.data = []

        onWillStart(async () => {
            const response = await this.orm.call('fast.blank.packing_list_detail', 'get_rep_size_list', [], {})
            this.sizeList = response.data
            console.log(this.sizeList)
            const number = response.data.t.length - response.data.s.length
            if (number > 0) {
                this.sizeS = new Array(Math.abs(number)).fill('th');
            } else {
                this.sizeT = new Array(Math.abs(number)).fill('th');
            }


            const rest = await this.orm.call('fast.blank.packing_list_detail', 'packing_list_difference', [], {})
            let value = JSON.parse(rest)
            console.log(value)
            this.data = value.data
            console.log(this.data)
        })

        onMounted(() => {
            console.log('onMounted')
            console.log(this.state.selects)

            // // 已知数据渲染
            // var inst = layui.table.render({
            //     elem: '#ID-table-demo-data',
            //     url: '/api/packing_list_difference',
            //     parseData: function (res) { // res 即为原始返回的数据
            //         return {
            //             "code": res.code,
            //             "msg": res.msg,
            //             "data": res.data[0]
            //         };
            //     },
            //     //skin: 'line', // 表格风格
            //     //even: true,
            //     page: true, // 是否显示分页
            //     limits:
            //         [5, 10, 15],
            //     limit:
            //         5 // 每页默认显示的数量
            // });
        })

        onWillUpdateProps(() => {
            console.log('onWillUpdateProps')
        })

        onRendered(() => {
            console.log('onRendered')
        })

        whenReady(() => {
            console.log('whenReady    当 DOM 加载完成时再执行')
        })
    }
}

ReportFormsTree
    .template = 'Report.FormsTree'

registry
    .category(
        "actions"
    ).add(
    "reportForms"
    ,
    ReportFormsTree
)
