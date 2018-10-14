import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { NotificationService } from '@heartsteps/notifications/notification.service';
import { MessageReceiptService } from '@heartsteps/notifications/message-receipt.service';



@NgModule({
    imports: [
        InfrastructureModule
    ],
    providers: [
        NotificationService,
        MessageReceiptService
    ]
})
export class NotificationsModule {}
