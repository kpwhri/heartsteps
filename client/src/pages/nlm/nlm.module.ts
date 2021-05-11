import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { BlankPage } from './blank-page';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { IonicPageModule } from 'ionic-angular';

const nlmRoutes: Routes = [
  {
    path: 'nlm',
    component: BlankPage
  }
];

@NgModule({
  declarations: [
    BlankPage
  ],
  entryComponents: [
    BlankPage
  ],
  imports: [
    HeartstepsComponentsModule,
    IonicPageModule.forChild(BlankPage),
    RouterModule.forChild(nlmRoutes)
  ],
  exports: [
    RouterModule
  ]
})
export class NLMModule { }
