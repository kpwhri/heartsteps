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

const settingsRoutes: Routes = [
    {
        path: 'settings/contact',
        component: ContactPage
    }, {
        path: 'settings/places',
        component: PlacesPage
    }, {
        path: 'settings/reflection-time',
        component: ReflectionTimePage
    }, {
        path: 'settings/suggestion-times',
        component: SuggestionTimesPage
    }, {
        path: 'settings/weekly-goal',
        component: GoalPage
    }
]

@NgModule({
    declarations: [
        SettingsPage,
        SuggestionTimesPage,
        ContactPage,
        PlacesPage,
        ReflectionTimePage,
        GoalPage
    ],
    entryComponents: [
        SettingsPage
    ],
    exports: [
        RouterModule
    ],
    imports: [
        ContactInformationModule,
        PlacesModule,
        WeeklySurveyModule,
        WalkingSuggestionsModule,
        RouterModule.forChild(settingsRoutes)
    ],
})
export class SettingsModule {}
