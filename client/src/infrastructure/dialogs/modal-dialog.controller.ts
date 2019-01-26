import { Injectable } from "@angular/core";
import { ModalController } from "ionic-angular";


@Injectable()
export class ModalDialogController {

    constructor(
        private modalCtrl: ModalController
    ) {}

    public createModal(component: any, data?:any): Promise<any> {
        return new Promise((resolve) => {
            const modal = this.modalCtrl.create(component, data);
            modal.onDidDismiss((data) => {
                resolve(data);
            })
            modal.present();
        });
    }

}
