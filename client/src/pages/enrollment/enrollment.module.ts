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
import { InfrastructureModule } from "@infrastructure/infrastructure.module";
import { SetupPageModule } from "@pages/setup/setup.module";

const enrollmentRoutes: Routes = [
    {
        path: 'welcome',
        component: WelcomePageComponent
    }, {
        path: 'login',
        component: EnrollmentPage
    }, {
        path: 'enroll',
        component: EnrollmentPage
    }
];


@NgModule({
    declarations: [
        EnrollmentPage,
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
        SetupPageModule,
        ReactiveFormsModule,
        InfrastructureModule,
        RouterModule.forChild(enrollmentRoutes)
    ]
})
export class EnrollmentModule {}
