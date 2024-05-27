/** @odoo-module */

import {registry} from "@web/core/registry"
import {useService} from "@web/core/utils/hooks";

const {Component, whenReady, useRef, onRendered, onWillUpdateProps, onMounted, useState} = owl;

export class ReportFormsTree extends Component {
    setup() {
        this.orm = useService("orm");
        this.user = useService("user");
        this.notification = useService("notification");
        this.action = useService("action");
        this.state = useState({
            selects: [],
            data: [],
        })

        onMounted(() => {
            console.log('onMounted')
            console.log(this.state.selects)

            // 已知数据渲染
            var inst = layui.table.render({
                elem: '#ID-table-demo-data',
                data: [{ // 赋值已知数据
                    "id": "10001",
                    "username": "张三1",
                    "sex": "男",
                    "city": "浙江杭州",
                    "sign": "人生恰似一场修行",
                    "experience": "116"
                }, {
                    "id": "10002",
                    "username": "张三2",
                    "sex": "男",
                    "city": "浙江杭州",
                    "sign": "人生恰似一场修行",
                    "experience": "12",
                    "LAY_CHECKED": true
                }],
                //skin: 'line', // 表格风格
                //even: true,
                page: true, // 是否显示分页
                limits: [5, 10, 15],
                limit: 5 // 每页默认显示的数量
            });
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

ReportFormsTree.template = 'Report.FormsTree'

registry.category("actions").add("reportForms", ReportFormsTree)
