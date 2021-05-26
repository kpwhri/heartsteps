import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { IonicPageModule } from 'ionic-angular';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { FitbitService } from './fitbit.service';
import { FitbitApp } from './fitbit-app';




@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
        IonicPageModule.forChild(FitbitApp)
    ],
    providers: [
        FitbitService
    ],
    declarations: [
        FitbitApp
    ],
    exports: [
        FitbitApp
    ]
})
export class FitbitModule {}
