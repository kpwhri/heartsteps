import { NgModule } from '@angular/core';
import { BaselineWeekGaurd } from './baseline-week.gaurd'
import { BaselineWeekPage } from './baseline-week.page'
import { ParticipantModule } from '@heartsteps/participants/participant.module';
import { Routes, RouterModule } from '@angular/router';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { BrowserModule } from '@angular/platform-browser';
import { DailySummaryModule } from '@heartsteps/daily-summaries/daily-summary.module';


const baselineRoutes: Routes = [{
    path: 'baseline',
    component: BaselineWeekPage,
    canActivate: [BaselineWeekGaurd]
}]

@NgModule({
    declarations: [
        BaselineWeekPage
    ],
    imports: [
        BrowserModule,
        DailySummaryModule,
        ParticipantModule,
        HeartstepsComponentsModule,
        RouterModule.forChild(baselineRoutes)
    ],
    providers: [
        BaselineWeekGaurd
    ]
})
export class BaselineWeekModule {}
