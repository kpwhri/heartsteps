import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { OnboardPage } from './onboard';
import { NotificationsScreen } from './notifications';

@NgModule({
  declarations: [
    OnboardPage,
    NotificationsScreen
  ],
  imports: [
    IonicPageModule.forChild(OnboardPage),
  ],
})
export class OnboardPageModule {}
