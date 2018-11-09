import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { WelcomePage } from './welcome';
import { ParticipantModule } from '@heartsteps/participants/participant.module';
import { EnrollmentModule } from '@heartsteps/enrollment/enrollment.module';

@NgModule({
  declarations: [
    WelcomePage
  ],
  imports: [
    ParticipantModule,
    EnrollmentModule,
    IonicPageModule.forChild(WelcomePage)
  ],
})
export class WelcomePageModule {}
