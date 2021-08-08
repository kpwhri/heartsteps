import { NgModule } from '@angular/core';
import { UserLogsPage } from './user-logs.page'
import { ParticipantModule } from '@heartsteps/participants/participant.module';
import { Routes, RouterModule } from '@angular/router';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { BrowserModule } from '@angular/platform-browser';


const userLogRoutes: Routes = [{
    path: 'userLogs',
    component: UserLogsPage
}]

@NgModule({
    declarations: [
        UserLogsPage
    ],
    imports: [
        BrowserModule,
        ParticipantModule,
        HeartstepsComponentsModule
    ]
})
export class UserLogsModule {}
