import { Component } from "@angular/core";
import { ViewController, NavParams } from "ionic-angular";
import { MessageReceiptService } from "@heartsteps/notifications/message-receipt.service";
import { Notification } from "@heartsteps/notifications/notification.model";


@Component({
    templateUrl: 'notification.html'
})
export class NotificationPane {

    public body: string;
    private notification: Notification;

    constructor(
        private messageReceiptService: MessageReceiptService,
        private viewCtrl:ViewController,
        params:NavParams
    ) {
        this.notification = params.get('notification');
        this.body = this.notification.body;

        this.messageReceiptService.opened(this.notification.id);
    }

    dismiss() {
        this.messageReceiptService.engaged(this.notification.id);
        this.viewCtrl.dismiss();
    }
}