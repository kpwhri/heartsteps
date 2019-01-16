import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { MorningSurveyPage } from './morning-survey.page';
import { MorningMessageModule } from '@heartsteps/morning-message/morning-message.module';
import { BrowserModule } from '@angular/platform-browser';
import { MorningMessageResolver } from './morning-message.resolver';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { StartPageComponent } from './start.page';
import { SurveyPageComponent } from './survey.page';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';

const morningSurveyRoutes: Routes = [{
    path: 'morning-survey/:page',
    component: MorningSurveyPage,
    resolve: {
        morningMessage: MorningMessageResolver
    }
}, {
    path: 'morning-survey',
    redirectTo: 'morning-survey/start'
}]

@NgModule({
    declarations: [
        MorningSurveyPage,
        StartPageComponent,
        SurveyPageComponent
    ],
    entryComponents: [
        StartPageComponent,
        SurveyPageComponent
    ],
    providers: [
        MorningMessageResolver
    ],
    imports: [
        BrowserModule,
        InfrastructureModule,
        HeartstepsComponentsModule,
        MorningMessageModule,
        RouterModule.forChild(morningSurveyRoutes)
    ],
    exports: [
        RouterModule
    ]
})
export class MorningSurveyPageModule {}
