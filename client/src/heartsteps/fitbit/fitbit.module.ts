import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { IonicPageModule } from 'ionic-angular';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { FitbitAuth } from './fitbit-auth';
import { FitbitService } from './fitbit.service';
import { FitbitApp } from './fitbit-app';




@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
        IonicPageModule.forChild(FitbitAuth),
        IonicPageModule.forChild(FitbitApp)
    ],
    providers: [
        FitbitService
    ],
    declarations: [
        FitbitAuth,
        FitbitApp
    ],
    exports: [
        FitbitApp,
        FitbitAuth
    ]
})
export class FitbitModule {}
