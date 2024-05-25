/** @odoo-module **/

import { registry } from "@web/core/registry";
const viewRegistry = registry.category("views");

import { FllowTreeController } from "@fast_supplier_synergy/js/fllow_tree/fllow_tree_controller"
import { FllowTreeRender } from "@fast_supplier_synergy/js/fllow_tree/fllow_tree_render"
import { FllowTreeModel } from "@fast_supplier_synergy/js/fllow_tree/fllow_tree_model"
import { FllowTreeArchParser } from "@fast_supplier_synergy/js/fllow_tree/fllow_tree_arch_parser"


export const FllowTreeView = {
    type: "fllow_tree",
    display_name: "FllowTree",
    icon: "fa fa-table",
    Controller: FllowTreeController,
    Renderer: FllowTreeRender,
    Model: FllowTreeModel,
    ArchParser: FllowTreeArchParser,
    // multiRecord: true,
    searchMenuTypes: ["filter"],
    buttonTemplate: "fast_supplier_synergy.fllow_tree.Buttons",

    props: (genericProps, view) => {
        const { ArchParser } = view;
        const { arch, relatedModels, resModel, fields } = genericProps;
        const archInfo = new ArchParser().parse(arch, relatedModels, resModel);
        let modelParams = {
            fieldAttrs: archInfo.fieldAttrs,
            fields: fields,
            groupBy: archInfo.groupBy,
            resModel: resModel,
            limit: archInfo.limit || 80,
        };
        return {
            ...genericProps,
            modelParams,
            Model: view.Model,
            Renderer: view.Renderer,
            buttonTemplate: view.buttonTemplate,
        };
    },
};

registry.category("views").add("fllow_tree", FllowTreeView);