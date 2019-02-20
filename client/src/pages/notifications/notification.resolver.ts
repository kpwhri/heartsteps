import { Injectable } from "@angular/core";
import { Resolve, ActivatedRouteSnapshot } from "@angular/router";

import { Message } from "@heartsteps/notifications/message.model";
import { MessageService } from "@heartsteps/notifications/message.service";


@Injectable()
export class NotificationResolver implements Resolve<Message> {

    constructor(
        private messageService:MessageService
    ){}

    resolve(route:ActivatedRouteSnapshot) {
        return this.messageService.getMessage(route.paramMap.get('notificationId'));
    }
}
