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
    }
]

@NgModule({
    declarations: [
        SettingsPage,
        SuggestionTimesPage,
        ContactPage,
        PlacesPage,
        ReflectionTimePage,
        NotificationsPage,
        GoalPage
    ],
    entryComponents: [
        SettingsPage
    ],
    exports: [
        RouterModule
    ],
    imports: [
        AntiSedentaryModule,
        BrowserModule,
        ContactInformationModule,
        HeartstepsComponentsModule,
        PlacesModule,
        WeeklySurveyModule,
        WalkingSuggestionsModule,
        NotificationsModule,
        RouterModule.forChild(settingsRoutes)
    ],
})
export class SettingsModule {}
