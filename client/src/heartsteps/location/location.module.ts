import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { LocationsService } from './locations.service';
import { LocationEdit } from './location-edit';
import { BrowserModule } from '@angular/platform-browser';
import { IonicPageModule } from 'ionic-angular';

@NgModule({
  imports: [
    BrowserModule,
    InfrastructureModule,
    IonicPageModule.forChild(LocationEdit)
  ],
  declarations: [
    LocationEdit
  ],
  exports: [
    LocationEdit
  ],
  providers: [
      LocationsService
  ]
})
export class LocationModule {}
