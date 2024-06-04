/** @odoo-module */

import {registry} from "@web/core/registry";
import {RelationalModel} from "@web/views/relational_model";
import { XMLParser } from "@web/core/utils/xml";


import { both_tree_controller } from "./both_tree_controller";
import { both_tree_renderer } from "./both_tree_renderer";
export const bothTree = {
    type: "both_tree",
    display_name: "both_tree",
    icon: "fa fa-star",
    Controller: both_tree_controller,
    Renderer: both_tree_renderer,
    ArchParser: XMLParser,
    Model: RelationalModel,
    searchMenuTypes: ["filter"],
    multiRecord: true,
    buttonTemplate: 'harvest_end.both_tree_view.Buttons',

    props: (genericProps, view) => {
        return {
            ...genericProps,
            buttonTemplate: view.buttonTemplate,
            Model: view.Model,
            Renderer: view.Renderer,
        };
    },
};
registry.category("views").add("both_tree", bothTree);
