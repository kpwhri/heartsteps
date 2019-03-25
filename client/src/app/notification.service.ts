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
            console.log('AppNotificationService: Processing message id=' + message.id);
            this.processOpenedMessage(message)
            .then(() => {
                console.log('AppNotificationService: Opened message id='+message.id)
                message.opened();
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
                console.log('AppNotificationService: Try to open notification page for: ' + message.id);
                return this.router.navigate(['notification', message.id]);
        }
    }
}
