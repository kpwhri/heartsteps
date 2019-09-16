import { NgModule } from "@angular/core";
import { WelcomePageComponent } from "./welcome.page";
import { RouterModule, Routes } from "@angular/router";
import { EnrollmentPage } from "./enrollment.page";
import { HeartstepsComponentsModule } from "@infrastructure/components/components.module";
import { FormModule } from "@infrastructure/form/form.module";
import { ReactiveFormsModule } from "@angular/forms";
import { EnrollmentModule as HeartstepsEnrollmentModule } from "@heartsteps/enrollment/enrollment.module";
import { ParticipantModule } from "@heartsteps/participants/participant.module";
import { CurrentWeekModule } from "@heartsteps/current-week/current-week.module";
import { SetupPage } from "./setup.page";
import { CompletePage } from "./complete.page";
import { EnrollmentGaurd } from "./enrollment.gaurd";
import { InfrastructureModule } from "@infrastructure/infrastructure.module";

const enrollmentRoutes: Routes = [{
    path: 'complete',
    component: CompletePage,
    canActivate: [EnrollmentGaurd]
}, {
    path: 'welcome',
    component: WelcomePageComponent
}, {
    path: 'login',
    component: EnrollmentPage
}, {
    path: 'enroll',
    component: EnrollmentPage
}, {
    path: 'setup/:page',
    component: SetupPage,
    canActivate: [EnrollmentGaurd]
}, {
    path: 'setup',
    pathMatch: 'full',
    redirectTo: 'setup/start'
}];


@NgModule({
    declarations: [
        CompletePage,
        EnrollmentPage,
        SetupPage,
        WelcomePageComponent
    ],
    exports: [
        RouterModule
    ],
    imports: [
        HeartstepsComponentsModule,
        HeartstepsEnrollmentModule,
        FormModule,
        ParticipantModule,
        CurrentWeekModule,
        ReactiveFormsModule,
        InfrastructureModule,
        RouterModule.forChild(enrollmentRoutes)
    ],
    providers: [
        EnrollmentGaurd
    ]
})
export class EnrollmentModule {}
