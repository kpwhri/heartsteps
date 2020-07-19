import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SettingsPage } from './settings-page';
import { ContactPage } from './contact-page';
import { ContactInformationModule } from '@heartsteps/contact-information/contact-information.module';
import { PlacesPage } from './places-page';
import { PlacesModule } from '@heartsteps/places/places.module';
import { ReflectionTimePage } from './reflection-time-page';
import { WeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module';
import { SuggestionTimesPage } from './suggestion-times';
import { WalkingSuggestionsModule } from '@heartsteps/walking-suggestions/walking-suggestions.module';
import { GoalPage } from './goal.page';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { AntiSedentaryModule } from '@heartsteps/anti-sedentary/anti-sedentary.module';
import { BrowserModule } from '@angular/platform-browser';
import { NotificationsPage } from './notifications.page';
import { NotificationsModule } from '@heartsteps/notifications/notifications.module';
import { SettingsComponent } from './settings.component';
import { FitbitAuthorizationPage } from './fitbit-authorization.page';
import { FitbitModule } from '@heartsteps/fitbit/fitbit.module';
import { FitbitWatchPage } from './fitbit-watch.page';
import { FitbitWatchModule } from '@heartsteps/fitbit-watch/fitbit-watch.module';
import { ActivitySurveysModule } from '@heartsteps/activity-surveys/activity-surveys.module';
import { FitbitClockFacePinPage } from './fitbit-clock-face-pin.page';
import { FormModule } from '@infrastructure/form/form.module';
import { ReactiveFormsModule } from '@angular/forms';

const settingsRoutes: Routes = [
    {
        path: 'settings/contact',
        component: ContactPage,
        outlet: 'modal'
    }, {
        path: 'settings/places',
        component: PlacesPage,
        outlet: 'modal'
    }, {
        path: 'settings/reflection-time',
        component: ReflectionTimePage,
        outlet: 'modal'
    }, {
        path: 'settings/suggestion-times',
        component: SuggestionTimesPage,
        outlet: 'modal'
    }, {
        path: 'settings/weekly-goal',
        component: GoalPage,
        outlet: 'modal'
    }, {
        path: 'settings/notifications',
        component: NotificationsPage,
        outlet: 'modal'
    },
    {
        path: 'settings/fitbit-authorization',
        component: FitbitAuthorizationPage,
        outlet: 'modal'
    },
    {
        path: 'settings/fitbit-watch',
        component: FitbitWatchPage,
        outlet: 'modal'
    },
    {
        path: 'settings/fitbit-clock-face-pin',
        component: FitbitClockFacePinPage,
        outlet: 'modal'
    },
    {
        path: 'settings',
        component: SettingsPage
    }
]

@NgModule({
    declarations: [
        SettingsComponent,
        SettingsPage,
        SuggestionTimesPage,
        ContactPage,
        PlacesPage,
        ReflectionTimePage,
        NotificationsPage,
        GoalPage,
        FitbitAuthorizationPage,
        FitbitWatchPage,
        FitbitClockFacePinPage
    ],
    entryComponents: [
        SettingsPage
    ],
    exports: [
        RouterModule
    ],
    imports: [
        ActivitySurveysModule,
        AntiSedentaryModule,
        BrowserModule,
        ContactInformationModule,
        FitbitWatchModule,
        FormModule,
        ReactiveFormsModule,
        HeartstepsComponentsModule,
        PlacesModule,
        FitbitModule,
        WeeklySurveyModule,
        WalkingSuggestionsModule,
        NotificationsModule,
        RouterModule.forChild(settingsRoutes)
    ],
})
export class SettingsModule {}
