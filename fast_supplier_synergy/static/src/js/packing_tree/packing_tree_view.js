/** @odoo-module **/

import { registry } from "@web/core/registry";
const viewRegistry = registry.category("views");

import { PackingTreeController } from "@fast_supplier_synergy/js/packing_tree/packing_tree_controller"
import { PackingTreeRender } from "@fast_supplier_synergy/js/packing_tree/packing_tree_render"
import { PackingTreeModel } from "@fast_supplier_synergy/js/packing_tree/packing_tree_model"
import { PackingTreeArchParser } from "@fast_supplier_synergy/js/packing_tree/packing_tree_arch_parser"


export const PackingTreeView = {
    type: "packing_tree",
    display_name: "PackingTree",
    icon: "fa fa-table",
    Controller: PackingTreeController,
    Renderer: PackingTreeRender,
    Model: PackingTreeModel,
    ArchParser: PackingTreeArchParser,
    // multiRecord: true,
    searchMenuTypes: ["filter"],
    buttonTemplate: "fast_supplier_synergy.packing_tree.Buttons",

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

registry.category("views").add("packing_tree", PackingTreeView);