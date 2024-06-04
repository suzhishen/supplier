/** @odoo-module **/

import { KeepLast, Race } from "@web/core/utils/concurrency";
import { Model } from "@web/views/model";
import { useState, onWillStart, useEffect, onWillUpdateProps } from "@odoo/owl";

export class PackingTreeModel extends Model{
    setup(params){
        this.keepLast = new KeepLast();
        this.race = new Race();
        this.offset = 0;
        this.limit = params.limit;
        this.state = useState({
        })
        // this.dataRecord = {}
        const _fetchDataPoints = this._fetchDataPoints.bind(this);
        this._fetchDataPoints = (...args) => {
            return this.race.add(_fetchDataPoints(...args));
        };

        onWillStart(async ()=>{
            await this.fetchCount(this.env.searchModel);
        })
        onWillUpdateProps(async (newProps)=>{
            await this.fetchCount(newProps);
        })
    }

    async _fetchDataPoints(metaData) {
        const result = await this.keepLast.add(this._loadDataPoints(metaData));
        this.ormDatas = result.result;
        this.metaData = metaData;
        this._prepareData(result);
    }

    _prepareData(result){
        this.state.order_datas = this.ormDatas
        this.state.foot_order_line_total = result.foot_order_line_total
        this.state.foot_incoming_line_total = result.foot_incoming_line_total
        this.state.foot_incomplete_line_total = result.foot_incomplete_line_total
    }

    async _loadDataPoints(metaData) {
        const { domain, fields, groupBy, resModel } = metaData;
        console.log(metaData)
        let result = this.orm.call(resModel,  'get_fllow_tree_render_view_datas', [], {
            'domain': domain,
            'limit': this.limit,
            'offset': this.offset,
            'page_groupby': groupBy
        }).then((data) => {
            return data;
        })
        return result
    }

    async load(searchParams) {
        this.searchParams = searchParams;
        const { domain, context, groupBy } = this.searchParams;
        let metaData;
        metaData = {
            domain,
            groupBy,
            resModel: this.env.searchModel.resModel
        }
        return this._fetchDataPoints(metaData);
    }

    async fetchCount(params){
        const { domain, groupBy, resModel } = params;
        this.count = await this.orm.call(resModel,  'get_fllow_tree_count', [], {
            'domain': domain,
            'page_groupby': groupBy
        })
    }
}

