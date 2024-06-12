/** @odoo-module */

import {registry} from "@web/core/registry";
import {RelationalModel} from "@web/views/relational_model";
import {XMLParser} from "@web/core/utils/xml";

import {report_tree_controller} from "./report_tree_controller";
import {report_tree_renderer} from "./report_tree_renderer";

export const report_tree_view = {
    type: "report_tree",
    display_name: "report_tree",
    icon: "fa fa-indent",
    Controller: report_tree_controller,
    Renderer: report_tree_renderer,
    ArchParser: XMLParser,
    Model: RelationalModel,
    searchMenuTypes: [],
    // searchMenuTypes: ["filter"],
    multiRecord: true,
    buttonTemplate: 'fast_supplier_synergy.report_tree_view.Buttons',

    props: (genericProps, view) => {
        return {
            ...genericProps,
            buttonTemplate: view.buttonTemplate,
            Model: view.Model,
            Renderer: view.Renderer,
        };
    },
};
registry.category("views").add("report_tree", report_tree_view);
