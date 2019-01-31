import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { EnrollmentModal } from './enroll';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { EnrollmentController } from './enrollment.controller';
import { EnrollmentService } from './enrollment.service';
import { FormModule } from '@infrastructure/form/form.module';

@NgModule({
  declarations: [
    EnrollmentModal
  ],
  exports: [
    EnrollmentModal
  ],
  imports: [
    InfrastructureModule,
    FormModule,
    IonicPageModule.forChild(EnrollmentModal)
  ],
  providers: [
    EnrollmentController,
    EnrollmentService
  ]
})
export class EnrollmentModule {}
