import { NgModule } from '@angular/core';
import { ActivityPlansModule } from '@heartsteps/activity-plans/activity-plans.module';
import { Routes, RouterModule } from '@angular/router';
import { ActivityPlanPage } from './activity-plan.page';
import { ActivityPlanResolver } from './activity-plan.resolver';
import { DayPlanComponent } from './day-plan.component';
import { WeeklyPlanComponent } from './weekly-plan.component';
import { BrowserModule } from '@angular/platform-browser';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { ActivityPlanCompletePage } from './activity-plan-complete.page';
import { CreatePlanPage } from './create-plan.page';
import { PlanComponent } from './plan.component';
import { PlanFormComponent } from './plan-form.component';
import { ReactiveFormsModule } from '@angular/forms';
import { ActivityTypeModule } from '@heartsteps/activity-types/activity-types.module';
import { FormModule } from '@infrastructure/form/form.module';
import { CompletePlanResolver } from './complete-plan.resolver';
import { ActivityLogModule } from '@heartsteps/activity-logs/activity-logs.module';
import { CompletePlanForm } from './complete-plan-form.component';
import { ActivityPlanField } from './activity-plan-field.component';

const routes: Routes = [
    {
        path: 'plans/create/:date',
        component: CreatePlanPage
    }, {
        path: 'plans/:id/complete',
        component: ActivityPlanCompletePage,
        resolve: {
            activityPlan: CompletePlanResolver
        },
    }, {
        path: 'plans/:id',
        component: ActivityPlanPage,
        resolve: {
            activityPlan: ActivityPlanResolver
        },
    }
];

@NgModule({
    declarations: [
        ActivityPlanField,
        CreatePlanPage,
        DayPlanComponent,
        WeeklyPlanComponent,
        PlanComponent,
        PlanFormComponent,
        CompletePlanForm,
        ActivityPlanPage,
        ActivityPlanCompletePage
    ],
    entryComponents: [
        PlanComponent,
        PlanFormComponent,
        CompletePlanForm,
        DayPlanComponent,
        WeeklyPlanComponent
    ],
    exports: [
        PlanComponent,
        DayPlanComponent,
        RouterModule,
        WeeklyPlanComponent
    ],
    imports: [
        ActivityPlansModule,
        ActivityLogModule,
        HeartstepsComponentsModule,
        BrowserModule,
        FormModule,
        ReactiveFormsModule,
        ActivityTypeModule,
        RouterModule.forChild(routes)
    ],
    providers: [
        ActivityPlanResolver,
        CompletePlanResolver
    ]
})
export class ActivityPlanPageModule {}
