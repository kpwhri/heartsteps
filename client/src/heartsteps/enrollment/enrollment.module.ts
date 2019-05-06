import { NgModule } from '@angular/core';
import { EnrollmentModal } from './enroll';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { EnrollmentController } from './enrollment.controller';
import { EnrollmentService } from './enrollment.service';
import { FormModule } from '@infrastructure/form/form.module';
import { DialogsModule } from '@infrastructure/dialogs/dialogs.module';
import { ReactiveFormsModule } from '@angular/forms';

@NgModule({
  declarations: [
    EnrollmentModal
  ],
  exports: [
    EnrollmentModal
  ],
  imports: [
    InfrastructureModule,
    DialogsModule,
    FormModule,
    ReactiveFormsModule
  ],
  providers: [
    EnrollmentController,
    EnrollmentService
  ]
})
export class EnrollmentModule {}
