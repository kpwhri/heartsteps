import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { BrowserModule } from '@angular/platform-browser';
import { PlanComponent } from './plan.component';
import { DayPlanComponent } from './day-plan.component';
import { IonicPageModule } from 'ionic-angular';
import { ActivityPlanService } from './activity-plan.service';
import { PlanFormComponent } from './plan-form.component';
import { PlanModalComponent } from './plan-modal.component';
import { WeeklyPlanComponent } from './weekly-plan.component';
import { FormModule } from '@infrastructure/form/form.module';
import { ActivityTypeModule } from '@heartsteps/activity-types/activity-types.module';
import { DialogsModule } from '@infrastructure/dialogs/dialogs.module';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
        DialogsModule,
        FormModule,
        ActivityTypeModule,
        IonicPageModule.forChild(PlanFormComponent),
        IonicPageModule.forChild(PlanComponent),
        IonicPageModule.forChild(DayPlanComponent)
    ],
    declarations: [
        PlanFormComponent,
        PlanModalComponent,
        PlanComponent,
        DayPlanComponent,
        WeeklyPlanComponent
    ],
    exports: [
        PlanFormComponent,
        PlanComponent,
        DayPlanComponent,
        WeeklyPlanComponent
    ],
    entryComponents: [
        PlanModalComponent
    ],
    providers: [
        ActivityPlanService
    ]
})
export class ActivityPlansModule {}
