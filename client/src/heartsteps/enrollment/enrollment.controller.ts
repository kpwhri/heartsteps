import { Injectable } from "@angular/core";
import { ModalController } from "ionic-angular";
import { EnrollmentModal } from "./enroll";


@Injectable()
export class EnrollmentController {

    constructor(
        private modalCtrl: ModalController
    ){}

    public enroll(message:string, dismissable:boolean = true):Promise<boolean> {
        return new Promise((resolve, reject) => {
            const modal = this.modalCtrl.create(EnrollmentModal, {
                message: message
            }, {
                enableBackdropDismiss: dismissable
            })
            modal.onDidDismiss(() => {
                resolve(true);
            });
            modal.present();
        }) 
    }

}