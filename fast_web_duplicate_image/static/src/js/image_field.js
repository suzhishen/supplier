/** @odoo-module **/

import {registry} from '@web/core/registry';
import {ImageField} from '@web/views/fields/image/image_field';

import {onMounted, onWillUnmount} from "@odoo/owl";
import {browser} from "@web/core/browser/browser";

var session = require('web.session');
import {useService} from "@web/core/utils/hooks";


export class CopyImageField extends ImageField {
    setup() {
        super.setup();

        this.notification = useService("notification");
        this.WEB_COPY_IMAGE_SIZE = session.WEB_COPY_IMAGE_SIZE || 50 * 1024


        this.handlePaste = (e) => this.imageParser(e)
        onMounted(() => {
            browser.addEventListener('paste', this.handlePaste);
        })
        onWillUnmount(() => {
            browser.removeEventListener('paste', this.handlePaste)
        });

    }

    imageParser(e) {
        let self = this;
        if (!self.props.readonly) {
            let items = (e.clipboardData || e.originalEvent.clipboardData).items;
            if(items.length === 1){
                for (var i = 0; i < items.length; i++) {
                    if (items[i].type.indexOf('image') !== -1) {
                        var blob = items[i].getAsFile();
                        if (blob.size > self.WEB_COPY_IMAGE_SIZE) {
                            let msg = `当前图片大小[${(blob.size / 1024).toFixed(2)}KB]，超出图片大小限制[${self.formatNumberFast(self.WEB_COPY_IMAGE_SIZE / 1024)}KB]！`;
                            self.notification.add(msg, {
                                title: "上传出错",
                                type: 'danger'
                            })
                            break;
                        }
                        var reader = new FileReader();
                        reader.onload = function (event) {
                            self.clipboardImage = event.target.result;
                            self.state.isValid = true;
                            self.rawCacheKey = null;
                            self.props.update(self.clipboardImage.split(',')[1]);
                        };
                        reader.readAsDataURL(blob);
                    }
                }
            }
        }
    };

    formatNumberFast(num) {
        if (num === 0) {
            return 0;
        } else {
            return parseFloat(num.toString()).toString();
        }
    };
}

registry.category("fields").add("web_copy_image", CopyImageField);


import { patch } from "@web/core/utils/patch";

patch(ImageField.prototype, 'fast.ImageField', {

    setup(){
      this._super.apply();
      this.WEB_COPY_IMAGE_SIZE = session.WEB_COPY_IMAGE_SIZE || 50 * 1024
    },

    onFileUploaded(info) {
        if (info.size > this.WEB_COPY_IMAGE_SIZE) {
            let msg = `当前图片大小[${(info.size / 1024).toFixed(2)}KB]，
            超出图片大小限制[${this.formatNumberFast(this.WEB_COPY_IMAGE_SIZE / 1024)}KB]！`;
            this.notification.add(msg, {
                title: "上传出错",
                type: 'danger'
            })
        }
        else {
            return this._super.apply(this, arguments)
        }
    },

    formatNumberFast(num) {
        if (num === 0) {
            return 0;
        } else {
            return parseFloat(num.toString()).toString();
        }
    }

})