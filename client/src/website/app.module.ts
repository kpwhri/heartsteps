import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { IonicApp, IonicModule } from 'ionic-angular';

import { HeartstepsWebsite } from './website.component';
import { EnrollmentModule } from '@pages/enrollment/enrollment.module';
import { BrowserModule } from '@angular/platform-browser';

const appRoutes:Routes = [{
  path: '',
  redirectTo: 'welcome',
  pathMatch: 'full'
}]

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
            {
                useHash: true
            }
        )
    ],
    bootstrap: [IonicApp],
    entryComponents: [
        HeartstepsWebsite
    ]
})
export class AppModule {}
