import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { EnrollPage } from './enroll';

@NgModule({
  declarations: [
    EnrollPage,
  ],
  imports: [
    IonicPageModule.forChild(EnrollPage),
  ],
})
export class EnrollPageModule {}
