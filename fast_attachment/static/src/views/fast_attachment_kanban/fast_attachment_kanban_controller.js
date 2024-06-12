/** @odoo-module **/

import {KanbanController} from "@web/views/kanban/kanban_controller";
import {useBus, useService} from "@web/core/utils/hooks";

const {useRef} = owl;

export class FastAttachmentKanbanController extends KanbanController {
    setup() {
        super.setup(...arguments);
        this.uploadFileInput = useRef("uploadFileInput");
        this.uploadService = useService("file_upload");
        useBus(
            this.uploadService.bus,
            "FILE_UPLOAD_LOADED",
            () => {
                this.model.load();
            },
        );
    }

    async onInputChange(ev) {
        if (!ev.target.files) {
            return;
        }
        this.uploadService.upload(
            "/web/binary/upload_attachment",
            ev.target.files,
            {
                buildFormData: (formData) => {
                    let active_model = this.props.context.active_model ? this.props.context.active_model : ''
                    let active_id = this.props.context.active_id ? this.props.context.active_id : 0
                    let categ_id = this.props.context.default_categ_id ? this.props.context.default_categ_id : false
                    // let upload_file_to_oos = this.props.context.default_upload_file_to_oos ? this.props.context.default_upload_file_to_oos : false
                    formData.append("model", active_model);
                    formData.append("id", active_id);
                    formData.append("categ_id", categ_id);
                    // formData.append("upload_file_to_oos", upload_file_to_oos);
                },
            },
        );
        ev.target.value = "";
    }
}
