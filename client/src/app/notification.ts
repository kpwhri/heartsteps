import { Component } from "@angular/core";
import { ViewController, NavParams } from "ionic-angular";
import { MessageReceiptService } from "@heartsteps/notifications/message-receipt.service";


@Component({
    templateUrl: 'notification.html'
})
export class NotificationPane {

    public message: string;
    private messageId: string;

    constructor(
        private messageReceiptService: MessageReceiptService,
        private viewCtrl:ViewController,
        params:NavParams
    ) {
        this.message = params.get('message');
        this.messageId = params.get('messageId');

        if(this.messageId) {
            this.messageReceiptService.opened(this.messageId);
        }
    }

    dismiss() {
        this.messageReceiptService.engaged(this.messageId);
        this.viewCtrl.dismiss();
    }
}