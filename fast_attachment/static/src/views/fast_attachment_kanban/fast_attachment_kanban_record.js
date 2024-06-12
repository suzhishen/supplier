/** @odoo-module **/

import { CANCEL_GLOBAL_CLICK, KanbanRecord } from "@web/views/kanban/kanban_record";
import { useService } from "@web/core/utils/hooks";

export class FastAttachmentKanbanRecord extends KanbanRecord {
    setup() {
        super.setup()
        this.messaging = useService("messaging");
    }

    openAttachmentList(){
        this.messaging.get().then((messaging) => {
            const attachmentList = messaging.models["AttachmentList"].insert({
                selectedAttachment: messaging.models["Attachment"].insert({
                    id: this.props.record.data.id,
                    filename: this.props.record.data.name,
                    name: this.props.record.data.name,
                    mimetype: this.props.record.data.mimetype,
                }),
            });
            this.dialog = messaging.models["Dialog"].insert({
                attachmentListOwnerAsAttachmentView: attachmentList,
            });
        });
        return;
    }
    /**
     * @override
     *
     * Override to open the preview upon clicking the image, if compatible.
     */
    onGlobalClick(ev) {
        if (ev.target.classList.contains('o_attachment_image')) {
            return this.openAttachmentList();
        }
        else if(ev.target.classList.contains('o_image_thumbnail')){
            // let node = $(ev.target).attr('data-mimetype');
            return this.openAttachmentList();
        }
        return super.onGlobalClick(...arguments);
    }
}
