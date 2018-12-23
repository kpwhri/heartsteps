import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { EnrollmentModal } from './enroll';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { EnrollmentController } from './enrollment.controller';
import { EnrollmentService } from './enrollment.service';

@NgModule({
  declarations: [
    EnrollmentModal
  ],
  exports: [
    EnrollmentModal
  ],
  imports: [
    InfrastructureModule,
    IonicPageModule.forChild(EnrollmentModal)
  ],
  providers: [
    EnrollmentController,
    EnrollmentService
  ]
})
export class EnrollmentModule {}
