import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { PlacesList } from './places-list';
import { PlaceEdit } from './place-edit';
import { PlacesService } from './places.service';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';


@NgModule({
  providers: [
    PlacesService
  ],
  declarations: [
    PlacesList,
    PlaceEdit
  ],
  exports: [
    PlacesList,
    PlaceEdit
  ],
  imports: [
    InfrastructureModule,
    IonicPageModule.forChild(PlaceEdit),
    IonicPageModule.forChild(PlacesList)
  ]
})
export class PlacesModule {}
