import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { BrowserModule } from '@angular/platform-browser';
import { PlanComponent } from './plan.component';
import { ActivityPlanService } from './activity-plan.service';
import { PlanFormComponent } from './plan-form.component';
import { FormModule } from '@infrastructure/form/form.module';
import { ActivityTypeModule } from '@heartsteps/activity-types/activity-types.module';
import { DialogsModule } from '@infrastructure/dialogs/dialogs.module';
import { ActivityLogModule } from '@heartsteps/activity-logs/activity-logs.module';
import { ReactiveFormsModule } from '@angular/forms';

@NgModule({
    declarations: [
        PlanFormComponent,
        PlanComponent
    ],
    exports: [
        PlanFormComponent,
        PlanComponent
    ],
    imports: [
        InfrastructureModule,
        BrowserModule,
        DialogsModule,
        FormModule,
        ReactiveFormsModule,
        ActivityTypeModule,
        ActivityLogModule
    ],
    providers: [
        ActivityPlanService
    ]
})
export class ActivityPlansModule {}
