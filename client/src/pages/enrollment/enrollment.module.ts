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

const enrollmentRoutes: Routes = [{
    path: 'complete',
    component: CompletePage
}, {
    path: 'welcome',
    component: WelcomePageComponent
}, {
    path: 'enroll',
    component: EnrollmentPage
}, {
    path: 'setup/:page',
    component: SetupPage
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
        RouterModule.forChild(enrollmentRoutes)
    ]
})
export class EnrollmentModule {}
