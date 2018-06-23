import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { EnrollPage } from './enroll';
import { HeartstepsModule } from '../../heartsteps/heartsteps.module';
import { HomePageModule } from '../home/home.module';

@NgModule({
  declarations: [
    EnrollPage
  ],
  imports: [
    HomePageModule,
    HeartstepsModule,
    IonicPageModule.forChild(EnrollPage)
  ],
})
export class EnrollPageModule {}
