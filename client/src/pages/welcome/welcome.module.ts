import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { WelcomePage } from './welcome';
import { ParticipantModule } from '@heartsteps/participants/participant.module';
import { EnrollmentModule } from '@heartsteps/enrollment/enrollment.module';
import { RouterModule, Routes } from '@angular/router';
import { EnrollPageComponent } from './enroll.page';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { WelcomeGuard } from './welcome.guard';

const welcomeRoutes: Routes = [{
    path: 'welcome',
    canActivate: [WelcomeGuard],
    component: WelcomePage
}, {
    path: 'enroll',
    canActivate: [WelcomeGuard],
    component: EnrollPageComponent,
    outlet: 'modal'
}];

@NgModule({
    declarations: [
        WelcomePage,
        EnrollPageComponent
    ],
    imports: [
        HeartstepsComponentsModule,
        ParticipantModule,
        EnrollmentModule,
        IonicPageModule.forChild(WelcomePage),
        RouterModule.forChild(welcomeRoutes)
    ],
    exports: [
        RouterModule
    ],
    providers: [
        WelcomeGuard
    ]
})
export class WelcomePageModule {}
