import { NgModule } from '@angular/core';
import { NotificationsModule as HeartstepsNotificationsModule } from '@heartsteps/notifications/notifications.module';
import { RouterModule, Routes } from '@angular/router';
import { NotificationPage } from './notification.page';
import { NotificationResolver } from './notification.resolver';
import { BrowserModule } from '@angular/platform-browser';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';

const notificationRoutes: Routes = [{
    path: 'notification/:notificationId',
    component: NotificationPage
}];

@NgModule({
    declarations: [
        NotificationPage
    ],
    providers: [
        NotificationResolver
    ],
    imports: [
        BrowserModule,
        HeartstepsComponentsModule,
        HeartstepsNotificationsModule,
        RouterModule.forChild(notificationRoutes)
    ],
    exports: [
        RouterModule
    ]
})
export class NotificationsModule {}
