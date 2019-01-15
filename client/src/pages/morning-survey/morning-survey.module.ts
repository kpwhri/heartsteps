import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { MorningSurveyPage } from './morning-survey.page';
import { MorningMessageModule } from '@heartsteps/morning-message/morning-message.module';
import { BrowserModule } from '@angular/platform-browser';
import { MorningMessageResolver } from './morning-message.resolver';

const morningSurveyRoutes: Routes = [{
    path: 'morning-survey',
    component: MorningSurveyPage,
    resolve: {
        morningMessage: MorningMessageResolver
    }
}]

@NgModule({
    declarations: [
        MorningSurveyPage
    ],
    entryComponents: [
    ],
    providers: [
        MorningMessageResolver
    ],
    imports: [
        BrowserModule,
        MorningMessageModule,
        RouterModule.forChild(morningSurveyRoutes)
    ],
    exports: [
        RouterModule
    ]
})
export class MorningSurveyPageModule {}
