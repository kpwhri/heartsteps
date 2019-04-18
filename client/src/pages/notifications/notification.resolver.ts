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
        console.log('NotificationResolver: Resolving route...');
        return this.messageService.getMessage(route.paramMap.get('notificationId'))
        .then((message) => {
            console.log('NotificationResolver: got message id='+message.id);
            return message;
        })
        .catch(() => {
            console.log('NotificationResolver: There was an error');
            return Promise.reject('Error getting message');
        });
    }
}
