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
            console.log("src", "heartsteps", "enrollment", "enrollment.controller", "enroll", "message", message);
            console.log("src", "heartsteps", "enrollment", "enrollment.controller", "enroll", 1);
            const modal = this.modalCtrl.create(EnrollmentModal, {
                message: message
            }, {
                enableBackdropDismiss: dismissable
            })
            console.log("src", "heartsteps", "enrollment", "enrollment.controller", "enroll", 2);
            modal.onDidDismiss(() => {
                resolve(true);
            });
            console.log("src", "heartsteps", "enrollment", "enrollment.controller", "enroll", 3);
            modal.present();
            console.log("src", "heartsteps", "enrollment", "enrollment.controller", "enroll", 4);
        }) 
    }

}