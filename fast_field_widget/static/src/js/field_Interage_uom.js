/** @odoo-module **/

import { IntegerField } from "@web/views/fields/integer/integer_field";
import { formatInteger } from "@web/views/fields/formatters";
import { registry } from "@web/core/registry";

export class UomInt extends IntegerField {
    get formattedValue() {
        if (!this.props.readonly && this.props.inputType === "number") {
            return this.props.value;
        }
        let value =  formatInteger(this.props.value);
        if(this.props.uomField && this.props.readonly){
            const fieldType = this.props.record.fields[this.props.uomField].type
            if(fieldType == 'char'){
                let fieldValue = this.props.record.data[this.props.uomField]
                if(fieldValue){
                    value = `${value} ${fieldValue}`
                }
            }
            else if(fieldType == 'many2one'){
                let fieldValue = this.props.record.data[this.props.uomField][1]
                if(fieldValue){
                    value = `${value} ${fieldValue}`
                }
            }
        }
        return value
    }
}

UomInt.template = "web.IntegerField";
UomInt.props = {
    ...IntegerField.props,
    uomField: { type: String, optional: true },
};

UomInt.supportedTypes = ["integer"];
UomInt.extractProps = ({ attrs, field }) => {
    return {
        ...IntegerField.extractProps({ attrs, field }),
        uomField: attrs.options.uomField,
    };
};

registry.category("fields").add("uom_int", UomInt);
