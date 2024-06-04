/** @odoo-module */

import {Component, onMounted, onWillStart, onWillUpdateProps, useState, useEffect, xml} from "@odoo/owl";


export class both_tree_renderer extends Component {
    setup() {
        this.orm = this.props.list.model.orm
        this.sizeList = {}
        this.sizeS = []
        this.sizeT = []
        this.list = useState({
            records: this.props.list.records
        })

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
        })
        useEffect(() => {
            this.list.records = this.props.list.records
        }, () => [this.props.list.records])
    }
}


both_tree_renderer.template = `harvest_end.both_tree_renderer`;


