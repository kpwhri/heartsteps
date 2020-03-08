import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Message } from "@heartsteps/notifications/message.model";
import { MessageService } from "@heartsteps/notifications/message.service";

@Injectable()
export class ActivitySurveyService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private messageService: MessageService
    ) {}

    public sendTestActivitySurvey(): Promise<Message> {
        return this.heartstepsServer.post('/activity-survey/test', {})
        .then((data) => {
            return this.messageService.loadMessage(data.notificationId);
        });
    }

}