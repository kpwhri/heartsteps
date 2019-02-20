import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { NotificationsModule as HeartstepsNotificationsModule } from '@heartsteps/notifications/notifications.module';
import { RouterModule, Routes } from '@angular/router';
import { NotificationPage } from './notification.page';
import { NotificationResolver } from './notification.resolver';

const notificationRoutes: Routes = [{
    path: 'notification/:notificationId',
    component: NotificationPage,
    resolve: {
        notification: NotificationResolver
    }
}];

@NgModule({
    declarations: [
        NotificationPage
    ],
    providers: [
        NotificationResolver
    ],
    imports: [
        HeartstepsNotificationsModule,
        IonicPageModule.forChild(NotificationPage),
        RouterModule.forChild(notificationRoutes)
    ],
    exports: [
        RouterModule
    ]
})
export class NotificationsModule {}
