import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { LocationsService } from './locations.service';

@NgModule({
  imports: [
    InfrastructureModule,
  ],
  providers: [
      LocationsService
  ]
})
export class LocationModule {}
