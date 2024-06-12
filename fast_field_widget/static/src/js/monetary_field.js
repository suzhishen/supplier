/** @odoo-module **/

import {localization as l10n} from "@web/core/l10n/localization";
import {registry} from "@web/core/registry";
import {escape, intersperse, nbsp, sprintf} from "@web/core/utils/strings";
import {session} from "@web/session";
import {markup} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";
import {MonetaryField} from "@web/views/fields/monetary/monetary_field";
import {patch} from "@web/core/utils/patch";

function insertThousandsSep(number, thousandsSep = ",", grouping = []) {
    const negative = number[0] === "-";
    number = negative ? number.slice(1) : number;
    return (negative ? "-" : "") + intersperse(number, grouping, thousandsSep);
}

function fastNumber(number, options = {decimals: 0, minDigits: 1}) {
    const decimals = options.decimals || 0;
    const minDigits = options.minDigits || 1;
    const d2 = Math.pow(10, decimals);
    const numberMagnitude = +number.toExponential().split("e+")[1];
    number = Math.round(number * d2) / d2;
    // the case numberMagnitude >= 21 corresponds to a number
    // better expressed in the scientific format.
    if (numberMagnitude >= 21) {
        // we do not use number.toExponential(decimals) because we want to
        // avoid the possible useless O decimals: 1e.+24 preferred to 1.0e+24
        number = Math.round(number * Math.pow(10, decimals - numberMagnitude)) / d2;
        return `${number}e+${numberMagnitude}`;
    }
    // note: we need to call toString here to make sure we manipulate the resulting
    // string, not an object with a toString method.
    const unitSymbols = _t("kMGTPE").toString();
    const sign = Math.sign(number);
    number = Math.abs(number);
    let symbol = "";
    for (let i = unitSymbols.length; i > 0; i--) {
        const s = Math.pow(10, i * 3);
        if (s <= number / Math.pow(10, minDigits - 1)) {
            number = Math.round((number * d2) / s) / d2;
            symbol = unitSymbols[i - 1];
            break;
        }
    }
    const {decimalPoint, grouping, thousandsSep} = l10n;

    // determine if we should keep the decimals (we don't want to display 1,020.02k for 1020020)
    const decimalsToKeep = number >= 1000 ? 0 : decimals;
    number = sign * number;
    const [integerPart, decimalPart] = number.toFixed(decimalsToKeep).split(".");
    const int = insertThousandsSep(integerPart, thousandsSep, grouping);
    if (!decimalPart) {
        return int + symbol;
    }
    return int + decimalPoint + decimalPart + symbol;
}

export function formatFloat(value, options = {}) {
    if (value === false) {
        return "";
    }
    if (options.humanReadable) {
        return fastNumber(value, options);
    }
    const grouping = options.grouping || l10n.grouping;
    const thousandsSep = "thousandsSep" in options ? options.thousandsSep : l10n.thousandsSep;
    const decimalPoint = "decimalPoint" in options ? options.decimalPoint : l10n.decimalPoint;
    let precision;
    if (options.digits && options.digits[1] !== undefined) {
        precision = options.digits[1];
    } else {
        precision = 2;
    }
    const formatted = (value || 0).toFixed(precision).split(".");
    formatted[0] = insertThousandsSep(formatted[0], thousandsSep, grouping);
    formatted[1] = formatted[1].replace(/0+$/, "");
    if (options.noTrailingZeros) {
        formatted[1] = formatted[1].replace(/0+$/, "");
    }
    return formatted[1] ? formatted.join(decimalPoint) : formatted[0];
}

registry.category("formatters").remove("float")
registry
    .category("formatters")
    .add("float", formatFloat)

export function formatMonetary(value, options = {}) {
    // Monetary fields want to display nothing when the value is unset.
    // You wouldn't want a value of 0 euro if nothing has been provided.
    if (value === false) {
        return "";
    }

    let currencyId = options.currencyId;
    if (!currencyId && options.data) {
        const currencyField =
            options.currencyField ||
            (options.field && options.field.currency_field) ||
            "currency_id";
        const dataValue = options.data[currencyField];
        currencyId = Array.isArray(dataValue) ? dataValue[0] : dataValue;
    }
    const currency = session.currencies[currencyId];
    const digits = options.digits || (currency && currency.digits);

    let formattedValue;
    if (options.humanReadable) {
        formattedValue = fastNumber(value, {decimals: digits ? digits[1] : 2});
    } else {
        formattedValue = formatFloat(value, {digits});
    }

    if (!currency || options.noSymbol) {
        return formattedValue;
    }
    const formatted = [currency.symbol, formattedValue];
    if (currency.position === "after") {
        formatted.reverse();
    }
    return formatted.join(nbsp);
}

registry.category("formatters").remove("monetary")
registry.category("formatters").add("monetary", formatMonetary)

//to override Monetary widget -- it use formatMonetary
patch(MonetaryField.prototype, 'fast_field_widget.MonetaryField', {
    get formattedValue() {
        if (this.props.inputType === "number" && !this.props.readonly && this.props.value) {
            return this.props.value;
        }
        return formatMonetary(this.props.value, {
            digits: this.currencyDigits,
            currencyId: this.currencyId,
            noSymbol: !this.props.readonly || this.props.hideSymbol,
        });
    }
})