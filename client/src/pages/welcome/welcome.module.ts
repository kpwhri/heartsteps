import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { WelcomePage } from './welcome';
import { ParticipantModule } from '@heartsteps/participants/participant.module';
import { EnrollmentModule } from '@heartsteps/enrollment/enrollment.module';
import { RouterModule, Routes } from '@angular/router';

const welcomeRoutes: Routes = [{
  path: 'welcome',
  component: WelcomePage
}];

@NgModule({
  declarations: [
    WelcomePage
  ],
  imports: [
    ParticipantModule,
    EnrollmentModule,
    IonicPageModule.forChild(WelcomePage),
    RouterModule.forChild(welcomeRoutes)
  ],
  exports: [
    RouterModule
  ]
})
export class WelcomePageModule {}
