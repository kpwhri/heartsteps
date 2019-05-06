import { NgModule } from '@angular/core';
import { OnboardPage } from './onboard';
import { WalkingSuggestionsModule } from '@heartsteps/walking-suggestions/walking-suggestions.module';
import { WeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module';
import { PlacesModule } from '@heartsteps/places/places.module';
import { ParticipantModule } from '@heartsteps/participants/participant.module';
import { NotificationsModule } from '@heartsteps/notifications/notifications.module';
import { FitbitModule } from '@heartsteps/fitbit/fitbit.module';
import { ContactInformationModule } from '@heartsteps/contact-information/contact-information.module';
import { Routes, RouterModule } from '@angular/router';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { OnboardGaurd } from './onboard.gaurd';
import { FitbitWatchModule } from '@heartsteps/fitbit-watch/fitbit-watch.module';

const onboardRoutes:Routes = [
    {
        path: 'onboard/:page',
        canActivate: [OnboardGaurd],
        component: OnboardPage
    }, {
        path: 'onboard',
        canActivate: [OnboardGaurd],
        pathMatch: 'full',
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
        FitbitModule,
        FitbitWatchModule,
        ContactInformationModule,
        WalkingSuggestionsModule,
        RouterModule.forChild(onboardRoutes)
    ],
    exports: [
        RouterModule
    ],
    providers: [
        OnboardGaurd
    ]
})
export class OnboardPageModule {}
