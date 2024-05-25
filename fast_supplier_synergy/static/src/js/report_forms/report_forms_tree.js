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
        })

        onWillUpdateProps(() => {
            console.log('onWillUpdateProps')
        })

        onRendered(() => {
            console.log('onRendered')
        })

        whenReady(() => {
            console.log('whenReady    当 DOM 加载完成时再执行')

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
                }, {
                    "id": "10003",
                    "username": "张三3",
                    "sex": "男",
                    "city": "浙江杭州",
                    "sign": "人生恰似一场修行",
                    "experience": "65"
                }, {
                    "id": "10004",
                    "username": "张三4",
                    "sex": "男",
                    "city": "浙江杭州",
                    "sign": "人生恰似一场修行",
                    "experience": "777"
                }, {
                    "id": "10005",
                    "username": "张三5",
                    "sex": "男",
                    "city": "浙江杭州",
                    "sign": "人生恰似一场修行",
                    "experience": "86"
                }, {
                    "id": "10006",
                    "username": "张三6",
                    "sex": "男",
                    "city": "浙江杭州",
                    "sign": "人生恰似一场修行",
                    "experience": "12"
                }, {
                    "id": "10007",
                    "username": "张三7",
                    "sex": "男",
                    "city": "浙江杭州",
                    "sign": "人生恰似一场修行",
                    "experience": "16"
                }, {
                    "id": "10008",
                    "username": "张三8",
                    "sex": "男",
                    "city": "浙江杭州",
                    "sign": "人生恰似一场修行",
                    "experience": "106"
                }],
                //skin: 'line', // 表格风格
                //even: true,
                page: true, // 是否显示分页
                limits: [5, 10, 15],
                limit: 5 // 每页默认显示的数量
            });
        })
    }
}

ReportFormsTree.template = 'Report.FormsTree'

registry.category("actions").add("reportForms", ReportFormsTree)
