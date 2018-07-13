import { Component } from "@angular/core";
import { ViewController, NavParams } from "ionic-angular";


@Component({
    templateUrl: 'notification.html'
})
export class NotificationPane {

    private message:string

    constructor(private viewCtrl:ViewController, private params:NavParams) {

        this.message = params.get('message');

    }

    dismiss() {
        this.viewCtrl.dismiss();
    }
}