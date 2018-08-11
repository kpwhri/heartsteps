import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { WelcomePage } from './welcome';
import { EnrollPageModule } from '../enroll/enroll.module';

@NgModule({
  declarations: [
    WelcomePage
  ],
  imports: [
    EnrollPageModule,
    IonicPageModule.forChild(WelcomePage)
  ],
})
export class WelcomePageModule {}
