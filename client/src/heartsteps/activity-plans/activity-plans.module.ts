import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { ActivityPlanService } from './activity-plan.service';
import { ActivityTypeModule } from '@heartsteps/activity-types/activity-types.module';
import { DialogsModule } from '@infrastructure/dialogs/dialogs.module';
import { ActivityLogModule } from '@heartsteps/activity-logs/activity-logs.module';

@NgModule({
    imports: [
        InfrastructureModule,
        DialogsModule,
        ActivityTypeModule,
        ActivityLogModule
    ],
    providers: [
        ActivityPlanService
    ]
})
export class ActivityPlansModule {}
