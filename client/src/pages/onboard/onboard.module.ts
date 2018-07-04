import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { OnboardPage } from './onboard';
import { NotificationsPage } from './notifications';

@NgModule({
  declarations: [
    OnboardPage,
    NotificationsPage
  ],
  entryComponents: [
    NotificationsPage
  ],
  imports: [
    IonicPageModule.forChild(OnboardPage)
  ],
})
export class OnboardPageModule {}
