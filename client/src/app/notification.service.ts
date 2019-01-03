import { Injectable } from "@angular/core";
import { NotificationService as HeartstepsNotificationService } from '@heartsteps/notifications/notification.service';
import { NotificationService as InfrastructureNotificationService } from '@infrastructure/notification.service';
import { Notification } from "@heartsteps/notifications/notification.model";
import { WalkingSuggestionService } from "@heartsteps/walking-suggestions/walking-suggestion.service";
import { Router } from "@angular/router";
import { WeeklySurveyService } from "@heartsteps/weekly-survey/weekly-survey.service";

@Injectable()
export class NotificationService {
    
    constructor(
        private notifications: HeartstepsNotificationService,
        private notificationService: InfrastructureNotificationService,
        private walkingSuggestionService: WalkingSuggestionService,
        private weeklySurveyService: WeeklySurveyService,
        private router: Router
    ) {}

    setup() {

        this.notificationService.notification.subscribe((notification) => {
            if(notification.type === 'weekly-reflection') {
                this.weeklySurveyService.show();
            } else {
                console.log(notification);
            }
        });

        this.notificationService.setupNotificationListener();

        this.notifications.notificationMessage.subscribe((notification: Notification) => {
            this.router.navigate(['notification', notification.id]);
        });

        this.notifications.dataMessage.subscribe((payload:any) => {
            if(payload.type == 'weekly-reflection' && payload.weekId) {
                this.weeklySurveyService.set(payload.weekId);
            }
            if(payload.type == 'request-context' && payload.decisionId) {
                this.walkingSuggestionService.sendDecisionContext(payload.decisionId);
            }
        })
    }
}