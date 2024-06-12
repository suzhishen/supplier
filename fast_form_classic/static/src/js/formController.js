/** @odoo-module **/
import {FormController} from '@web/views/form/form_controller';
import {patch} from "@web/core/utils/patch";
import {FormArchParser} from "@web/views/form/form_arch_parser";
import {evalDomain} from "@web/views/utils";
import { archParseBoolean } from "@web/views/utils";

import { FormStatusIndicator } from "@web/views/form/form_status_indicator/form_status_indicator";
import {ConfirmationDialog} from "@web/core/confirmation_dialog/confirmation_dialog";

const {useRef, useEffect} = owl;


import { FormErrorDialog } from "@web/views/form/form_error_dialog/form_error_dialog";


export function getNewActiveActions(rootNode) {
    return {
        archive: archParseBoolean(rootNode.getAttribute("archive"), true),
        create_condition: rootNode.getAttribute("create_condition"),
        edit_condition: rootNode.getAttribute("edit_condition"),
        delete_condition: rootNode.getAttribute("delete_condition"),
        archive_condition: rootNode.getAttribute("archive_condition"),
        duplicate_condition: rootNode.getAttribute("duplicate_condition"),
    };
}

patch(FormArchParser.prototype, 'fast_form_classic.FormArchParser', {

    parse(arch, models, modelName) {
        let result = this._super.apply(this, arguments);
        result.disableAutofocus = true
        const activeActions = getNewActiveActions(result.xmlDoc);
        result.activeActions = Object.assign(result.activeActions, {
            ...activeActions
        })
        return result
    }

})

patch(FormController.prototype, 'fast.FormController', {
    setup() {
        this._super.apply();
        this.archInfo.disableAutofocus = true;
        if (!this.props.mode || !this.canEdit) {
            this.model.initialMode = 'readonly';
        }
        this.root = useRef("root");

        useEffect(
            (el) => {
                if (!el) {
                    return;
                }
                if (el.scrollTop > 0) {
                    el.scrollTop = 0
                }
            },
            () => [document.querySelector('.o_content')]
        );

        this.state.canCreate = this.canCreate
        this.state.canEdit = this.canEdit
        this.state.actionMenuItems = {}
        useEffect(() => {
            this.state.canCreate = this.canCreate
            this.state.canEdit = this.canEdit
            this.updateActionState()
        }, () => [this.model.root.data])
    },

    toggleButtonDisabled(){
        let buttons = document.querySelectorAll("button[disabled]")
        if(buttons.length > 0){
            buttons.forEach(el=>el.removeAttribute("disabled"))
        }
    },

    async discard() {
        let res = await this._super.apply();
        this.toggleButtonDisabled();
        return res
    },

    updateActionState() {
        if (this.archInfo.activeActions.create_condition) {
            let expr = this.archInfo.activeActions.create_condition
            let flag = evalDomain(expr, this.model.root.data)
            this.archInfo.activeActions['create'] = flag && this.state.canCreate
            this.state.canCreate = flag
            // this.canCreate = flag
        }
        if (this.archInfo.activeActions.edit_condition) {
            let expr = this.archInfo.activeActions.edit_condition
            let flag = evalDomain(expr, this.model.root.data) && this.state.canEdit
            this.archInfo.activeActions['edit'] = flag
            this.state.canEdit = flag
            // this.canEdit = flag
        }
        if (this.archInfo.activeActions.duplicate_condition) {
            let expr = this.archInfo.activeActions.duplicate_condition
            let flag = evalDomain(expr, this.model.root.data)
            this.archInfo.activeActions['duplicate'] = flag && this.state.canCreate
            this.getActionMenuItems()
        }
        if (this.archInfo.activeActions.delete_condition) {
            let expr = this.archInfo.activeActions.delete_condition
            let flag = evalDomain(expr, this.model.root.data)
            this.archInfo.activeActions['delete'] = flag
            this.getActionMenuItems()
        }
        if (!this.archInfo.activeActions.archive) {
            this.archiveEnabled = false
            this.getActionMenuItems()
        } else if (this.archInfo.activeActions.archive_condition) {
            let expr = this.archInfo.activeActions.archive_condition
            let flag = evalDomain(expr, this.model.root.data)
            this.archInfo.activeActions['archive'] = flag
            this.archiveEnabled = flag
            this.getActionMenuItems()
        } else {
            this.getActionMenuItems()
        }
    },

    getActionMenuItems() {
        let res = this._super.apply()
        this.state.actionMenuItems = res
        return this.state.actionMenuItems
    },

    async saveButtonClicked(params = {}) {
        let res = await this._super.apply()
        if (res && params && params.closable) {
            this.env.services.action.doAction({ type: "ir.actions.act_window_close" });
        }
        else if(res) {
            await this.model.root.switchMode("readonly");
            this.toggleButtonDisabled();
        }
        return res
    },

    async beforeLeave() {
        if (!this.model.root.isNew && this.model.root.mode === 'edit') {
            this.dialogService.add(ConfirmationDialog, {
                title:'数据未保存',
                body: "请先保存当前页面数据！",
                confirmLabel: '关闭',
                confirm: () => {
                    this.enableButtons()
                    return true
                }
            });
            return false
        }
        else{
            this._super.apply()
        }
    }
})


patch(FormStatusIndicator.prototype, 'fast.FormStatusIndicator', {

    async discard() {
        await this._super.apply()
        await this.props.model.root.switchMode("readonly")
    },
})