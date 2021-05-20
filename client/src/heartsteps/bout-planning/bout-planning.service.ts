import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Message } from "@heartsteps/notifications/message.model";
import { MessageService } from "@heartsteps/notifications/message.service";



@Injectable()
export class BoutPlanningService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private messageService: MessageService
    ) {}

    public sendTestMessage():Promise<Message> {
        return this.heartstepsServer.post('bout-planning/', {})
        .then((data) => {
            return this.messageService.loadMessage(data.messageId);
        });
    }

}
