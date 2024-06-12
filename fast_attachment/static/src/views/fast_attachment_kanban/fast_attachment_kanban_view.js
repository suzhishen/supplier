/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { FastAttachmentKanbanController } from "@fast_attachment/views/fast_attachment_kanban/fast_attachment_kanban_controller";
import { FastAttachmentKanbanRenderer } from "@fast_attachment/views/fast_attachment_kanban/fast_attachment_kanban_renderer";

export const FastAttachmentKanbanView = {
    ...kanbanView,
    Controller: FastAttachmentKanbanController,
    Renderer: FastAttachmentKanbanRenderer,
    buttonTemplate: "fast_attachment.FastAttachmentKanbanController.Buttons",
};
registry.category("views").add("fast_attachment_kanban_view_new", FastAttachmentKanbanView);
