import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { IonicApp, IonicModule } from 'ionic-angular';

import { HeartstepsWebsite } from './website.component';
import { EnrollmentModule } from '@pages/enrollment/enrollment.module';
import { BrowserModule } from '@angular/platform-browser';
import { AnalyticsService } from '@infrastructure/heartsteps/analytics.service';

declare var process: {
    env: {
        PRODUCTION: boolean
    }
}

const appRoutes:Routes = [{
  path: '',
  redirectTo: 'welcome',
  pathMatch: 'full'
}]

const routerOptions: any = {}
if (!process.env.PRODUCTION) {
    routerOptions.useHash = true;
}

@NgModule({
    declarations: [
        HeartstepsWebsite
    ],
    imports: [
        BrowserModule,
        EnrollmentModule,
        IonicModule.forRoot(HeartstepsWebsite),
        RouterModule.forRoot(
            appRoutes,
            routerOptions
        )
    ],
    bootstrap: [IonicApp],
    entryComponents: [
        HeartstepsWebsite
    ],
    providers: [
        AnalyticsService
    ]
})
export class AppModule {}
