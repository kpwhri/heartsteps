import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { IonicApp, IonicModule } from 'ionic-angular';

import { AnalyticsService } from '@infrastructure/heartsteps/analytics.service';
import { HeartstepsWebsite } from './app.component';

const appRoutes:Routes = [{
  path: '',
  redirectTo: '/home/dashboard',
  pathMatch: 'full'
}]

@NgModule({
  declarations: [
    HeartstepsWebsite
  ],
  imports: [
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
  ],
  providers: [
    AnalyticsService
  ]
})
export class AppModule {}
