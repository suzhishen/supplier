/** @odoo-module **/

import {FloatField} from "@web/views/fields/float/float_field";
import {formatFloat} from "@web/views/fields/formatters";
import {registry} from "@web/core/registry";
import {patch} from "@web/core/utils/patch";

function formatNumberFast(num) {
    let newstr = num;
    let leng = num.length - num.indexOf('.') - 1;
    if (num.indexOf('.') > -1) {
        for (let i = leng; i > 0; i--) {
            if (
                newstr.lastIndexOf('0') > -1 &&
                newstr.substr(newstr.length - 1, 1) == 0
            ) {
                let k = newstr.lastIndexOf('0');
                if (newstr.charAt(k - 1) == '.') {
                    return newstr.substring(0, k - 1);
                } else {
                    newstr = newstr.substring(0, k);
                }
            } else {
                return newstr;
            }
        }
    }
    return num;
}

export class UomFloat extends FloatField {
    get formattedValue() {
        if (this.props.inputType === "number" && !this.props.readonly && this.props.value) {
            return this.props.value;
        }
        let value = formatNumberFast(formatFloat(this.props.value, {digits: this.props.digits}));
        if (this.props.uomField && this.props.readonly) {
            const fieldType = this.props.record.fields[this.props.uomField].type
            if (fieldType == 'char') {
                let fieldValue = this.props.record.data[this.props.uomField]
                if (fieldValue) {
                    value = `${value} ${fieldValue}`
                }
            } else if (fieldType == 'many2one') {
                let fieldValue = this.props.record.data[this.props.uomField]
                if (fieldValue){
                    fieldValue = fieldValue[1]
                }
                if (fieldValue) {
                    value = `${value} ${fieldValue}`
                }
            }
        }
        return value
    }
}

UomFloat.template = "web.FloatField";
UomFloat.props = {
    ...FloatField.props,
    uomField: {type: String, optional: true},
};

UomFloat.supportedTypes = ["float"];
UomFloat.extractProps = ({attrs, field}) => {
    return {
        ...FloatField.extractProps({attrs, field}),
        uomField: attrs.options.uomField,
    };
};

registry.category("fields").add("uom_float", UomFloat);

patch(FloatField.prototype, 'fast_field_widget.FloatField', {
    get formattedValue() {
        if (this.props.inputType === "number" && !this.props.readonly && this.props.value) {
            return this.props.value;
        }
        let value = formatNumberFast(formatFloat(this.props.value, {digits: this.props.digits}));
        return value
    }
})
