import { NgModule } from '@angular/core';
import { PlacesList } from './places-list';
import { PlaceEdit } from './place-edit';
import { PlacesService } from './places.service';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { BrowserModule } from '@angular/platform-browser';
import { FormModule } from '@infrastructure/form/form.module';
import { FormsModule } from '@angular/forms';


@NgModule({
  providers: [
    PlacesService
  ],
  declarations: [
    PlacesList,
    PlaceEdit
  ],
  entryComponents: [
    PlaceEdit
  ],
  exports: [
    PlacesList,
    PlaceEdit
  ],
  imports: [
    BrowserModule,
    FormModule,
    FormsModule,
    HeartstepsComponentsModule,
    InfrastructureModule
  ]
})
export class PlacesModule {}
