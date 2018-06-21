import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';

import { IonicStorageModule } from '@ionic/storage';
import { EnrollmentService } from './enrollment.service';
import { AuthorizationService } from './authorization.service';

@NgModule({
  declarations: [
  ],
  imports: [
    HttpClientModule,
    IonicStorageModule.forRoot()
  ],
  entryComponents: [],
  providers: [
      EnrollmentService,
      AuthorizationService
  ]
})
export class HeartstepsModule {}
