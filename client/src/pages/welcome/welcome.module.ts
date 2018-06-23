import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { HeartstepsModule } from '../../heartsteps/heartsteps.module';
import { WelcomePage } from './welcome';
import { EnrollPageModule } from '../enroll/enroll.module';

@NgModule({
  declarations: [
    WelcomePage
  ],
  imports: [
    EnrollPageModule,
    HeartstepsModule,
    IonicPageModule.forChild(WelcomePage)
  ],
})
export class WelcomePageModule {}
