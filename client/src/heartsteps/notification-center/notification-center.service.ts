import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Notification } from "./Notification";
// import { Message } from "@heartsteps/notifications/message.model";
// import { MessageService } from "@heartsteps/notifications/message.service";

@Injectable()
export class NotificationCenterService {
    constructor(
        private heartstepsServer: HeartstepsServer // private messageService: MessageService
    ) {}

    public getRecentNotifications(): Promise<Notification[]> {
        return this.heartstepsServer.get("/notification_center/", {});
    }
}
