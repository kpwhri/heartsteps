import { Injectable } from "@angular/core";
import { MessageService } from '@heartsteps/notifications/message.service';
import { WalkingSuggestionService } from "@heartsteps/walking-suggestions/walking-suggestion.service";
import { Router } from "@angular/router";
import { WeeklySurveyService } from "@heartsteps/weekly-survey/weekly-survey.service";
import { Message } from "@heartsteps/notifications/message.model";
import { MorningMessageService } from "@heartsteps/morning-message/morning-message.service";

@Injectable()
export class NotificationService {
    
    constructor(
        private messageService: MessageService,
        private walkingSuggestionService: WalkingSuggestionService,
        private weeklySurveyService: WeeklySurveyService,
        private morningMessageService: MorningMessageService,
        private router: Router
    ) {}

    setup() {
        this.messageService.opened.subscribe((message: Message) => {
            this.processOpenedMessage(message)
            .then(() => {
                message.opened();
            });
        });
        this.messageService.received.subscribe((message:Message) => {
            this.processReceivedMessage(message)
            .then(() => {
                message.received();
            });
        });
        
        this.messageService.setup();
    }

    private processOpenedMessage(message: Message): Promise<boolean> {
        switch(message.type) {
            case 'weekly-reflection':
                return this.router.navigate(['weekly-survey']);
            case 'morning-message':
                return this.router.navigate(['morning-survey']);
            default:
                return this.router.navigate(['notification', message.id]);
        }
    }

    private processReceivedMessage(message: Message): Promise<boolean> {
        switch(message.type) {
            case 'weekly-reflection':
                return this.weeklySurveyService.processNotification(message);
            case 'morning-message':
                return this.morningMessageService.processMessage(message);
            case 'request-context':
                return this.walkingSuggestionService.sendDecisionContext(message.context.decisionId);
            default:
                return this.messageService.createNotification(message.id, message.body);
        }
    }
}