/** @odoo-module */
import { X2ManyField } from "@web/views/fields/x2many/x2many_field";
import { unique } from "@web/core/utils/arrays";
import { download } from "@web/core/network/download";
import { patch } from "@web/core/utils/patch";
import { onMounted, onWillUnmount } from "@odoo/owl";


patch(X2ManyField.prototype, 'fast.X2ManyField', {

    setup(){
        this._super.apply();
        if(this.activeField && this.activeField.rawAttrs.excel_download){
            this.showDownload = true;
        }
    },


    async downloadExport(fields, import_compat, format) {
        let ids = false;
        // if (!this.isDomainSelected) {
        //     const resIds = await this.getSelectedResIds();
        //     ids = resIds.length > 0 && resIds;
        // }
        const exportedFields = fields.map((field) => ({
            name: field.name || field.id,
            label: field.label || field.string,
            store: field.store,
            type: field.field_type || field.type,
        }));
        if (import_compat) {
            exportedFields.unshift({ name: "id", label: this.env._t("External ID") });
        }
        let records = this.props.value.currentIds
        await download({
            data: {
                data: JSON.stringify({
                    import_compat,
                    context: {},
                    domain: [['id', 'in', records]],
                    fields: exportedFields,
                    groupby: [],
                    ids,
                    model: this.activeField.relation,
                    filename: this.props.record.data.display_name || "",
                }),
            },
            url: `/web/export/${format}`,
        });
    },

    async onDirectExportData() {
        await this.downloadExport(this.defaultExportList, false, "xlsx");
    },

    get defaultExportList() {
        let list = unique(
                     this.activeField.views.list.columns
                .filter((col) => col.type === "field")
                .map((col) => this.props.value.fields[col.name])
                .filter((field) => field.exportable !== false)
        );
        return list;
    },
})