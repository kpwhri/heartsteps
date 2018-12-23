import { Injectable } from "@angular/core";
import { NotificationService as HeartstepsNotificationService } from '@heartsteps/notifications/notification.service';
import { Notification } from "@heartsteps/notifications/notification.model";
import { WalkingSuggestionService } from "@heartsteps/walking-suggestions/walking-suggestion.service";
import { Router } from "@angular/router";

@Injectable()
export class NotificationService {
    
    constructor(
        private notifications: HeartstepsNotificationService,
        private walkingSuggestionService: WalkingSuggestionService,
        private router: Router
    ) {}

    setup() {
        this.notifications.notificationMessage.subscribe((notification: Notification) => {
            this.router.navigate(['notification', notification.id]);
        });

        this.notifications.dataMessage.subscribe((payload:any) => {
            if(payload.type == 'request_context' && payload.decisionId) {
                this.walkingSuggestionService.sendDecisionContext(payload.decisionId);
            }
        })
    }
}