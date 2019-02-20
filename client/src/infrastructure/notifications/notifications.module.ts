import { NgModule } from "@angular/core";
import { PushNotificationService } from "./push-notification.service";
import { LocalNotificationService } from "./local-notification.service";


@NgModule({
    providers: [
        PushNotificationService,
        LocalNotificationService
    ]
})
export class NotificationsModule {}
