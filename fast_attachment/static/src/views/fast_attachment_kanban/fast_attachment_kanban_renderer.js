/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { FastAttachmentKanbanRecord } from "@fast_attachment/views/fast_attachment_kanban/fast_attachment_kanban_record";

export class FastAttachmentKanbanRenderer extends KanbanRenderer {
}

FastAttachmentKanbanRenderer.components = {
    ...KanbanRenderer.components,
    KanbanRecord: FastAttachmentKanbanRecord,
};
FastAttachmentKanbanRenderer.template = "web.KanbanRenderer";
