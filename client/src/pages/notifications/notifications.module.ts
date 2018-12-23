import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { NotificationsModule as HeartstepsNotificationsModule } from '@heartsteps/notifications/notifications.module';
import { RouterModule, Routes } from '@angular/router';
import { NotificationPage } from './notification.page';

const notificationRoutes: Routes = [{
  path: 'notification',
  component: NotificationPage
}];

@NgModule({
  declarations: [
    NotificationPage
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
