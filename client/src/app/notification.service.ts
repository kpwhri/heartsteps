import { Injectable } from "@angular/core";
import { MessageService } from '@heartsteps/notifications/message.service';
import { WalkingSuggestionService } from "@heartsteps/walking-suggestions/walking-suggestion.service";
import { Router } from "@angular/router";
import { WeeklySurveyService } from "@heartsteps/weekly-survey/weekly-survey.service";
import { Notification } from "@heartsteps/notifications/notification.model";
import { Message } from "@heartsteps/notifications/message.model";

@Injectable()
export class NotificationService {
    
    constructor(
        private messageService: MessageService,
        private walkingSuggestionService: WalkingSuggestionService,
        private weeklySurveyService: WeeklySurveyService,
        private router: Router
    ) {}

    setup() {
        this.messageService.opened.subscribe((message: Message) => {
            switch(message.type) {
                case 'weekly-reflection':
                    this.router.navigate(['weekly-survey', message.context.weekId])
                    break;
                case 'morning-message':
                    this.router.navigate(['morning-survey']);
                    break;
                default:
                    this.router.navigate(['notification', message.id]);
            }
        });
        this.messageService.received.subscribe((message:Message) => {
            switch(message.type) {
                case 'weekly-reflection':
                    this.weeklySurveyService.set(message.context.weekId);
                    this.messageService.createNotification(message.id, 'Take weekly survey');
                    break;
                case 'morning-message':
                    this.messageService.createNotification(message.id, 'Good morning');
                    break;
                case 'request-context':
                    this.walkingSuggestionService.sendDecisionContext(message.context.decisionId);
                    break;
                default:
                    this.messageService.createNotification(message.id, message.body);
            }
        });
        
        this.messageService.setup();
    }
}