import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
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
import { FitbitAuthorizePage } from "./fitbit-authorize.page";

const enrollmentRoutes: Routes = [
    {
        path: 'setup/complete',
        component: CompletePage,
        canActivate: [EnrollmentGaurd]
    }, {
        path: 'setup/fitbit-authorize',
        component: FitbitAuthorizePage,
        canActivate: [EnrollmentGaurd]
    }, {
        path: 'setup/:page',
        component: SetupPage,
        canActivate: [EnrollmentGaurd]
    }, {
        path: 'setup',
        pathMatch: 'full',
        redirectTo: 'setup/start'
    }
];


@NgModule({
    declarations: [
        CompletePage,
        FitbitAuthorizePage,
        SetupPage
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
export class SetupPageModule {}
