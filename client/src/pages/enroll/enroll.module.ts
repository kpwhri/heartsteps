import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { EnrollPage } from './enroll';
import { HeartstepsModule } from '../../heartsteps/heartsteps.module';

@NgModule({
  declarations: [
    EnrollPage
  ],
  imports: [
    HeartstepsModule,
    IonicPageModule.forChild(EnrollPage)
  ],
})
export class EnrollPageModule {}
