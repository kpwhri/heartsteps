import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { HeartstepsModule } from '../../heartsteps/heartsteps.module';
import { HomePage } from './home';

@NgModule({
  declarations: [
    HomePage
  ],
  imports: [
    HeartstepsModule,
    IonicPageModule.forChild(HomePage)
  ]
})
export class HomePageModule {}
