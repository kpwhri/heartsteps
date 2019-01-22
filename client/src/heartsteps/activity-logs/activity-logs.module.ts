import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { BrowserModule } from '@angular/platform-browser';
import { ActivityLogService } from './activity-log.service';
import { ActivityLogComponent } from './activity-log.component';
import { LogFormComponent } from './log-form.component';
import { ActivityModule } from '@heartsteps/activity/activity.module';
import { IonicPageModule } from 'ionic-angular';
import { FormModule } from '@infrastructure/form/form.module';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
        ActivityModule,
        FormModule,
        IonicPageModule.forChild(LogFormComponent)
    ],
    declarations: [
        ActivityLogComponent,
        LogFormComponent
    ],
    exports: [
        ActivityLogComponent,
        LogFormComponent
    ],
    providers: [
        ActivityLogService
    ]
})
export class ActivityLogModule {}
