import { Component, OnInit, Input } from "@angular/core";
import { ViewController } from "ionic-angular";

@Component({
    selector: 'app-modal-dialog',
    templateUrl: './modal-dialog.component.html'
})
export class ModalDialogComponent {

    @Input('title') title: string;

    constructor(
        private viewCtrl: ViewController
    ) {}

    public dismiss(data?: any) {
        this.viewCtrl.dismiss(data);
    }

}