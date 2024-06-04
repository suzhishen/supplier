/** @odoo-module */

import {Component, onWillStart} from "@odoo/owl";
import {Layout} from "@web/search/layout";
import {useModel} from "@web/views/model";
import {usePager} from "@web/search/pager_hook";
import {useService} from "@web/core/utils/hooks";
export class both_tree_controller extends Component {

    setup() {
        const fields = this.props.fields;
        this.showActiveItems = false
        this.orm = useService("orm");
        this.model = useModel(this.props.Model, {
            resModel: this.props.resModel,
            fields,
            viewMode: "both_tree",
        });


        usePager(() => {

            const list = this.model.root;
            const {count, limit, offset} = list;
            return {
                offset: offset,
                limit: limit,
                total: count,
                onUpdate: async ({offset, limit}, hasNavigated) => {
                    if (this.model.root.editedRecord) {
                        if (!(await this.model.root.editedRecord.save())) {
                            return;
                        }
                    }
                    await list.load({limit, offset});
                    this.render(true); // FIXME WOWL reactivity
                },
            };
        });
    }

    async onClickCreate() {
 await this.props.createRecord();
    }
    async downloadExcel(){
        var res_ids = []
        this.model.root.records.forEach((record)=>{
            res_ids.push(record.resId)
        })
        const action = await this.orm.call(this.props.resModel,'btn_download_data_excel',[[],res_ids],{})
        this.model.action.doAction(action)
    }
    get display() {
        const {controlPanel} = this.props.display;
        return {
            ...this.props.display,
            controlPanel: {
                ...controlPanel,
                showActiveItems:false
            },
        };
    }

}

both_tree_controller.template = `harvest_end.both_tree_view`;
both_tree_controller.components = {Layout};