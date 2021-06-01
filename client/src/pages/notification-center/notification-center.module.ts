import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { NotificationCenterPage } from './notification-center';

@NgModule({
  declarations: [
    NotificationCenterPage,
  ],
  imports: [
    IonicPageModule.forChild(NotificationCenterPage),
  ],
})
export class NotificationCenterPageModule {}
