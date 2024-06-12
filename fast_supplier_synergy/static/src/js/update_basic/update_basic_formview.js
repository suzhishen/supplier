/** @odoo-module **/

import {registry} from "@web/core/registry";
import {formView} from "@web/views/form/form_view";
import {FormController} from '@web/views/form/form_controller';
import {useService} from "@web/core/utils/hooks";

const {onWillStart, onMounted} = owl;


export class UpdateBasicFormController extends FormController {
    setup() {
        this.ormService = useService("orm");
        this.notification = useService("notification");
        super.setup();

        onMounted(async () => {
            let self = this
            console.log('通过接口更新基础资料数据')
            await this.ormService.call(this.props.resModel, 'update_basic_data', [], {'id': this.props.resId}).then(result => {
                if (result.code === 500) {
                    this.notification.add(
                        this.env._t(result.message),
                        {
                            title: '提示',
                            type: "warning",
                        }
                    );
                }
                self.model.load();
            })
            // await this.model.load();
        });
    }
}


export const UpdateBasicFormView = {
    ...formView,
    Controller: UpdateBasicFormController,
};

registry.category("views").add("update_basic_form", UpdateBasicFormView);
