import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { PlacesListPage } from '@pages/places/places-list';
import { PlaceEdit } from '@pages/places/place-edit';


@NgModule({
  declarations: [
    PlacesListPage,
    PlaceEdit
  ],
  entryComponents: [
    PlacesListPage
  ],
  imports: [
    IonicPageModule.forChild(PlaceEdit),
    IonicPageModule.forChild(PlacesListPage)
  ],
})
export class PlacesPageModule {}
