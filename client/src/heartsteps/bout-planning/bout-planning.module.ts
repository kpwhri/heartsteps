import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { IonicPageModule } from 'ionic-angular';
import { FirstBoutPlanningTimeService } from './first-bout-planning-time.service';
import { FirstBoutPlanningTimePage } from './first-bout-planning-time.page';
import { FormModule } from '@infrastructure/form/form.module';

@NgModule({
    imports: [
        InfrastructureModule,
        FormModule,
        BrowserModule,
        IonicPageModule.forChild(FirstBoutPlanningTimePage),
    ],
    providers: [
        FirstBoutPlanningTimeService,
    ],
    declarations: [
        FirstBoutPlanningTimePage,
    ],
    exports: [
        FirstBoutPlanningTimePage,
    ]
})
export class BoutPlanningModule {}
