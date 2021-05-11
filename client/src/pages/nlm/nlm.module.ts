import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { BlankPage } from './blank-page';
import { BoutPlanningModal } from './bout-planning-modal';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { IonicPageModule } from 'ionic-angular';

const nlmRoutes: Routes = [
  {
    path: 'nlm/blank',
    component: BlankPage,
    outlet: 'modal'
  },
  {
    path: 'nlm/bout-planning-modal',
    component: BoutPlanningModal,
    outlet: 'modal'
  }
];

@NgModule({
  declarations: [
    BlankPage,
    BoutPlanningModal
  ],
  entryComponents: [
    BlankPage,
    BoutPlanningModal
  ],
  imports: [
    HeartstepsComponentsModule,
    
    IonicPageModule.forChild(BlankPage),
    IonicPageModule.forChild(BoutPlanningModal),

    RouterModule.forChild(nlmRoutes)
  ],
  exports: [
    RouterModule
  ]
})
export class NLMModule { }
