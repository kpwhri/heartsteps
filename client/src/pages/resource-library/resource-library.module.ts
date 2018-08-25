import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ResourceLibraryPage } from './resource-library';

@NgModule({
  declarations: [
    ResourceLibraryPage,
  ],
  imports: [
    IonicPageModule.forChild(ResourceLibraryPage),
  ],
})
export class ResourceLibraryModule {}
