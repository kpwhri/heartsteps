import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { NotificationService } from '@heartsteps/notifications/notification.service';
import { MessageReceiptService } from '@heartsteps/notifications/message-receipt.service';
import { NotificationsPermission } from './notifications';



@NgModule({
    imports: [
        InfrastructureModule
    ],
    providers: [
        NotificationService,
        MessageReceiptService
    ],
    declarations: [
        NotificationsPermission
    ],
    exports: [
        NotificationsPermission
    ]
})
export class NotificationsModule {}
