/** @odoo-module **/
import {patch} from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ListRenderer } from "@web/views/list/list_renderer";
import { getTooltipInfo } from "@web/views/fields/field_tooltip";
import { evaluateExpr } from "@web/core/py_js/py";
import { getClassNameFromDecoration } from "@web/views/utils";
import { getFormattedValue } from "@web/views/utils";

const FIELD_CLASSES = {
    char: "o_list_char",
    float: "o_list_number",
    integer: "o_list_number",
    monetary: "o_list_number",
    text: "o_list_text",
    many2one: "o_list_many2one",
};

const FIXED_FIELD_COLUMN_WIDTHS = {
    boolean: "70px",
    date: "92px",
    datetime: "146px",
    float: "92px",
    integer: "74px",
    monetary: "104px",
    handle: "33px",
};

patch(ListRenderer.prototype, 'fast.ListRenderer.edit', {
    get getEmptyRowIds() {
        // let nbEmptyRow = Math.max(0, 4 - this.props.list.records.length);
        let nbEmptyRow = Math.max(0, 1 - this.props.list.records.length);
        if (nbEmptyRow > 0 && this.displayRowCreates) {
            nbEmptyRow -= 1;
        }
        return Array.from(Array(nbEmptyRow).keys());
    },

    //
    // // todo 待测试：因为在报价板块编辑状态下点击审核价格报错，修改了原生的一些判断如下
    // isSortable(column) {
    //     const { hasLabel, name } = column;
    //     if(this.fields.hasOwnProperty(name)){
    //         const { sortable } = this.fields[name];
    //         const { options } = this.props.list.activeFields[name];
    //         return (sortable || options.allow_order) && hasLabel;
    //     }
    //     else return false
    //
    // },
    //
    // isNumericColumn(column) {
    //     if(this.fields.hasOwnProperty(name)){
    //         const { type } = this.fields[column.name];
    //         return ["float", "integer", "monetary"].includes(type);
    //     }
    //     else return false
    //
    // },
    //
    // getCellClass(column, record) {
    //     if (!this.cellClassByColumn[column.id]) {
    //         const classNames = ["o_data_cell"];
    //         if (column.type === "button_group") {
    //             classNames.push("o_list_button");
    //         } else if (column.type === "field") {
    //             classNames.push("o_field_cell");
    //             if (
    //                 column.rawAttrs &&
    //                 column.rawAttrs.class &&
    //                 this.canUseFormatter(column, record)
    //             ) {
    //                 classNames.push(column.rawAttrs.class);
    //             }
    //             if(this.fields.hasOwnProperty(column.name)) {
    //                 const typeClass = FIELD_CLASSES[this.fields[column.name].type];
    //                 if (typeClass) {
    //                     classNames.push(typeClass);
    //                 }
    //             }
    //             if (column.widget) {
    //                 classNames.push(`o_${column.widget}_cell`);
    //             }
    //         }
    //         this.cellClassByColumn[column.id] = classNames;
    //     }
    //     const classNames = [...this.cellClassByColumn[column.id]];
    //     if (column.type === "field" && this.fields.hasOwnProperty(column.name)) {
    //         if (record.isRequired(column.name)) {
    //             classNames.push("o_required_modifier");
    //         }
    //         if (record.isInvalid(column.name)) {
    //             classNames.push("o_invalid_cell");
    //         }
    //         if (record.isReadonly(column.name)) {
    //             classNames.push("o_readonly_modifier");
    //         }
    //         if (this.canUseFormatter(column, record)) {
    //             // generate field decorations classNames (only if field-specific decorations
    //             // have been defined in an attribute, e.g. decoration-danger="other_field = 5")
    //             // only handle the text-decoration.
    //             const { decorations } = record.activeFields[column.name];
    //             for (const decoName in decorations) {
    //                 if (evaluateExpr(decorations[decoName], record.evalContext)) {
    //                     classNames.push(getClassNameFromDecoration(decoName));
    //                 }
    //             }
    //         }
    //         if (
    //             record.isInEdition &&
    //             this.props.list.editedRecord &&
    //             this.props.list.editedRecord.isReadonly(column.name)
    //         ) {
    //             classNames.push("text-muted");
    //         } else {
    //             classNames.push("cursor-pointer");
    //         }
    //     }
    //     return classNames.join(" ");
    // },
    //
    // makeTooltip(column) {
    //     if(this.fields.hasOwnProperty(column.name)) {
    //         return getTooltipInfo({
    //             viewMode: "list",
    //             resModel: this.props.list.resModel,
    //             field: this.props.list.fields[column.name],
    //             fieldInfo: this.props.list.activeFields[column.name],
    //         });
    //     }else return false
    // },
    //
    //  getCellTitle(column, record) {
    //     if (this.fields.hasOwnProperty(column.name)){
    //         const fieldType = this.fields[column.name].type;
    //         // Because we freeze the column sizes, it may happen that we have to shorten
    //         // field values. In order for the user to have access to the complete value
    //         // in those situations, we put the value as title of the cells.
    //         // This is only necessary for some field types, as for the others, we hardcode
    //         // a minimum column width that should be enough to display the entire value.
    //         // Also, we don't set title for json fields, because it's not human readable anyway.
    //         if (!(fieldType in FIXED_FIELD_COLUMN_WIDTHS) && fieldType != "json") {
    //             return this.getFormattedValue(column, record);
    //         }
    //     }
    //     else return ''
    //
    // },
    //
    // getFormattedValue(column, record) {
    //     if (this.fields.hasOwnProperty(column.name)){
    //         const fieldName = column.name;
    //         return getFormattedValue(record, fieldName, column.rawAttrs);
    //     }
    //     else return ''
    //
    // }
    // // todo 同上
})