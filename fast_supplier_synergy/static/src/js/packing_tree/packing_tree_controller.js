/** @odoo-module **/

import {Component, onWillStart, useSubEnv, useEffect, useRef, useState} from "@odoo/owl";
import {standardViewProps} from "@web/views/standard_view_props";
import { Layout } from "@web/search/layout";
import { useService, } from "@web/core/utils/hooks";
import { useModel } from "@web/views/model";
import { usePager } from "@web/search/pager_hook";
import { useSetupView } from "@web/views/view_hook";


export class PackingTreeController extends Component {
    setup() {
        this.ormService = useService("orm");
        this.actionService = useService("action");
        this.notification = useService('notification');
        this.rpcService = useService("rpc");
        this.model = useModel(this.props.Model, this.props.modelParams);
        useSetupView({
            rootRef: useRef("root"),
            getLocalState: () => {
                return { metaData: this.model.metaData };
            },
            getContext: () => this.getContext(),
        });

        usePager(() => {
            return {
                    offset: this.model.offset,
                    limit: this.model.limit,
                    total: this.model.count,
                    onUpdate: async ({ offset, limit }) => {
                        this.model.offset = offset;
                        this.model.limit = limit;
                        await this.model.load(this.props);
                        await this.onUpdatedPager();
                        this.render(true);
                    },
                    // updateTotal: hasLimitedCount ? () => root.fetchCount() : undefined,
                    // updateTotal: () => this.model.fetchCount(this.props),
                    updateTotal: undefined
                };
        });

    }

    async onUpdatedPager() {}

    getContext() {
        const { measure, groupBy, mode } = this.model.metaData;
        const context = {};
        return context;
    }

    async downloadExcel(){
        let result = await this.ormService.call(this.props.resModel, 'btn_download_data_excel', [[]], {
            download_datas: this.model.ormDatas
        })
        this.actionService.doAction(result);
    }

    // async create_package() {
    //     let result  = await this.rpcService('/erp/create_blank_package_list', {})
    //     console.log(result)
    // }
}

PackingTreeController.template = "fast_supplier_synergy.PackingTreeView";

PackingTreeController.components = { Layout };
PackingTreeController.props = {
    ...standardViewProps,
    Model: Function,
    Renderer: Function,
    modelParams: Object,
    buttonTemplate: String,
};