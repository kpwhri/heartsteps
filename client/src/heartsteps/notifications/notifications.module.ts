import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { NotificationsModule as InfrastructureNotificationsModule } from '@infrastructure/notifications/notifications.module'; 
import { MessageService } from '@heartsteps/notifications/message.service';
import { MessageReceiptService } from '@heartsteps/notifications/message-receipt.service';
import { NotificationsPermissionComponent } from './notification-permission.component';

@NgModule({
    imports: [
        InfrastructureModule,
        InfrastructureNotificationsModule
    ],
    providers: [
        MessageService,
        MessageReceiptService
    ],
    declarations: [
        NotificationsPermissionComponent
    ],
    exports: [
        NotificationsPermissionComponent
    ]
})
export class NotificationsModule {}
