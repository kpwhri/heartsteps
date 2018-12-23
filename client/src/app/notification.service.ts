import { Injectable } from "@angular/core";
import { NotificationService as HeartstepsNotificationService } from '@heartsteps/notifications/notification.service';
import { ModalController } from "ionic-angular";
import { NotificationPane } from "@app/notification";
import { Notification } from "@heartsteps/notifications/notification.model";
import { WalkingSuggestionService } from "@heartsteps/walking-suggestions/walking-suggestion.service";
import { Router } from "@angular/router";

@Injectable()
export class NotificationService {
    
    constructor(
        private notifications: HeartstepsNotificationService,
        private modalCtrl: ModalController,
        private walkingSuggestionService: WalkingSuggestionService,
        private router: Router
    ) {}

    setup() {
        this.notifications.notificationMessage.subscribe((notification: Notification) => {
            this.router.navigate(['notification']);
        });

        this.notifications.dataMessage.subscribe((payload:any) => {
            if(payload.type == 'request_context' && payload.decisionId) {
                this.walkingSuggestionService.sendDecisionContext(payload.decisionId);
            }
        })
    }

    showMessage(notification: Notification) {
        let modal = this.modalCtrl.create(NotificationPane, {
            notification: notification
        }, {
            showBackdrop: true,
            enableBackdropDismiss: true,
            cssClass: 'heartsteps-message-modal'
        });
        modal.present();
    }
}