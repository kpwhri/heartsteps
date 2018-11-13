import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { EnrollPage } from './enroll';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';

@NgModule({
  declarations: [
    EnrollPage
  ],
  exports: [
    EnrollPage
  ],
  imports: [
    InfrastructureModule,
    IonicPageModule.forChild(EnrollPage)
  ]
})
export class EnrollmentModule {}
