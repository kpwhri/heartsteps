import { NgModule } from '@angular/core';
import { OnboardPage } from './onboard';
import { WalkingSuggestionsModule } from '@heartsteps/walking-suggestions/walking-suggestions.module';
import { WeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module';
import { PlacesModule } from '@heartsteps/places/places.module';
import { ParticipantModule } from '@heartsteps/participants/participant.module';
import { NotificationsModule } from '@heartsteps/notifications/notifications.module';
import { LocationModule } from '@heartsteps/locations/location.module';
import { FitbitModule } from '@heartsteps/fitbit/fitbit.module';
import { ContactInformationModule } from '@heartsteps/contact-information/contact-information.module';
import { Routes, RouterModule } from '@angular/router';
import { AuthorizationGaurd } from '@heartsteps/participants/auth-gaurd.service';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';

const onboardRoutes:Routes = [
    {
        path: 'onboard/:page',
        component: OnboardPage,
        canActivate: [AuthorizationGaurd]
    }, {
        path: 'onboard',
        redirectTo: 'onboard/start'
    }
];

@NgModule({
  declarations: [
    OnboardPage,
  ],
  imports: [
    HeartstepsComponentsModule,
    WeeklySurveyModule,
    PlacesModule,
    ParticipantModule,
    NotificationsModule,
    LocationModule,
    FitbitModule,
    ContactInformationModule,
    WalkingSuggestionsModule,
    RouterModule.forChild(onboardRoutes)
  ],
  exports: [
    RouterModule
  ]
})
export class OnboardPageModule {}
