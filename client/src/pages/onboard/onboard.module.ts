import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { OnboardPage } from './onboard';
import { ActivitySuggestionsModule } from '@heartsteps/activity-suggestions/activity-suggestions.module';
import { WeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module';
import { PlacesModule } from '@heartsteps/places/places.module';
import { ParticipantModule } from '@heartsteps/participants/participant.module';
import { NotificationsModule } from '@heartsteps/notifications/notifications.module';
import { LocationModule } from '@heartsteps/locations/location.module';
import { FitbitModule } from '@heartsteps/fitbit/fitbit.module';
import { ContactInformationModule } from '@heartsteps/contact-information/contact-information.module';
import { Routes, RouterModule } from '@angular/router';

const onboardRoutes:Routes = [{
  path: 'onboard',
  component: OnboardPage
}]

@NgModule({
  declarations: [
    OnboardPage
  ],
  imports: [
    WeeklySurveyModule,
    PlacesModule,
    ParticipantModule,
    NotificationsModule,
    LocationModule,
    FitbitModule,
    ContactInformationModule,
    ActivitySuggestionsModule,
    IonicPageModule.forChild(OnboardPage),
    RouterModule.forChild(onboardRoutes)
  ],
  exports: [
    RouterModule
  ]
})
export class OnboardPageModule {}
