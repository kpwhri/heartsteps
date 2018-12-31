import { Injectable } from "@angular/core";
import { AlertController as IonicAlertController } from "ionic-angular";


@Injectable()
export class AlertDialogController {

    constructor(
        private alertCtrl:IonicAlertController
    ){}

    show(message:string):Promise<boolean> {
        return new Promise((resolve) => {
            const alert = this.alertCtrl.create({
                message: message,
                buttons: [{
                    text: 'Ok',
                    role: 'cancel',
                    handler: () => {
                        resolve(true);
                    }
                }]
            });
            alert.present();
        })
    }
}
