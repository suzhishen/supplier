/** @odoo-module **/

import { XMLParser } from "@web/core/utils/xml";

const ORDERS = ["ASC", "DESC", "asc", "desc", null];

export class ReportTreeArchParser extends XMLParser {
    parse(arch, fields = {}) {
        const archInfo = { fields, fieldAttrs: {}, groupBy: [] };
        let limit = 80;
        this.visitXML(arch, (node) => {
            switch (node.tagName) {
                case "fllow_tree": {
                    if (node.hasAttribute("limit")) {
                        limit = node.getAttribute("limit");
                        limit = limit &&  parseInt(limit, 10);
                        archInfo.limit = limit
                    }
                }
            }
        });
        return archInfo;
    }
}
