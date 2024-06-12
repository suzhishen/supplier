/** @odoo-module */

import { X2ManyField } from "@web/views/fields/x2many/x2many_field";
import { patch } from "@web/core/utils/patch";
import { useX2ManyCrud, useOpenX2ManyRecord, X2ManyFieldDialog } from "@web/views/fields/relational_utils";

patch(X2ManyField.prototype, 'fast_X2ManyField', {

    setup() {
        this._super();
        const { saveRecord, updateRecord, removeRecord } = useX2ManyCrud(
            () => this.list,
            this.isMany2Many
        );
        const openRecord = useOpenX2ManyRecord({
            resModel: this.list.resModel,
            activeField: this.activeField,
            activeActions: this.activeActions,
            getList: () => this.list,
            saveRecord,
            updateRecord,
            withParentId: this.activeField.widget !== "many2many",
        });
        this._openRecord = (params) => {
            const activeElement = document.activeElement;
            openRecord({
                ...params,
                onClose: () => {
                    this.close()
                    if (activeElement) {
                        activeElement.focus();
                    }
                },
            });
        };
    },

    async close(){
        if(this.props && this.props.record && this.props.record.mode === 'readonly' && this.props.value && this.props.value.model  && this.props.value.context && this.props.value.context.default_parent_res_id
            && this.props.value.context.force_refresh === 'refresh'){
            await this.props.value.model.load({'resId': this.props.value.context.default_parent_res_id});
            this.props.value.model.notify();
        }
    }

});