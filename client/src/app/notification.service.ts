import { Injectable } from "@angular/core";
import { NotificationService as HeartstepsNotificationService } from '@heartsteps/notification.service';
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Geolocation } from "@ionic-native/geolocation";
import { ModalController } from "ionic-angular";
import { NotificationPane } from "@app/notification";

@Injectable()
export class NotificationService {
    
    constructor(
        private notifications: HeartstepsNotificationService,
        private geolocation: Geolocation,
        private heartstepsServer: HeartstepsServer,
        private modalCtrl: ModalController
    ) {

        this.notifications.notificationMessage.subscribe((message:any) => {
            this.showMessage(message.body);
        });

        this.notifications.dataMessage.subscribe((payload:any) => {
            if(payload.type == 'get_context' && payload.decision_id) {
                this.geolocation.getCurrentPosition().then((position:Position) => {
                    this.heartstepsServer.post('/decisions/'+payload.decision_id, {
                        location: {
                            lat: position.coords.latitude,
                            lng: position.coords.longitude
                        }
                    })
                })
            }
        })
    }

    showMessage(message:string) {
        let modal = this.modalCtrl.create(NotificationPane, {
            message: message
        }, {
            showBackdrop: true,
            enableBackdropDismiss: true,
            cssClass: 'heartsteps-message-modal'
        })
        modal.present()
    }
}