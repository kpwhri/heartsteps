import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { BrowserModule } from '@angular/platform-browser';
import { ActivityLogService } from './activity-log.service';
import { ActivityLogComponent } from './activity-log.component';
import { LogFormComponent } from './log-form.component';
import { IonicPageModule } from 'ionic-angular';
import { FormModule } from '@infrastructure/form/form.module';
import { ActivityTypeModule } from '@heartsteps/activity-types/activity-types.module';
import { ActivityEnjoyedModalComponent } from './activity-enjoyed-modal.component';
import { DialogsModule } from '@infrastructure/dialogs/dialogs.module';
import { ActivityEnjoyedFieldComponent } from './activity-enjoyed-field.component';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
        ActivityTypeModule,
        DialogsModule,
        FormModule,
        IonicPageModule.forChild(LogFormComponent)
    ],
    declarations: [
        ActivityLogComponent,
        LogFormComponent,
        ActivityEnjoyedFieldComponent,
        ActivityEnjoyedModalComponent
    ],
    entryComponents: [
        ActivityEnjoyedModalComponent,
        ActivityEnjoyedFieldComponent
    ],
    exports: [
        ActivityLogComponent,
        LogFormComponent,
        ActivityEnjoyedFieldComponent,
        ActivityEnjoyedModalComponent
    ],
    providers: [
        ActivityLogService
    ]
})
export class ActivityLogModule {}
