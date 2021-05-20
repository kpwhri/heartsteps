import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { BlankPage } from './blank-page';
import { GenericMessagesModal } from './generic-messages-modal';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { IonicPageModule } from 'ionic-angular';

const nlmRoutes: Routes = [
  {
    path: 'nlm/blank',
    component: BlankPage,
    outlet: 'modal'
  },
  {
    path: 'nlm/generic-messages-modal',
    component: GenericMessagesModal,
    outlet: 'modal'
  }
];

@NgModule({
  declarations: [
    BlankPage,
    GenericMessagesModal
  ],
  entryComponents: [
    BlankPage,
    GenericMessagesModal
  ],
  imports: [
    HeartstepsComponentsModule,
    
    IonicPageModule.forChild(BlankPage),
    IonicPageModule.forChild(GenericMessagesModal),

    RouterModule.forChild(nlmRoutes)
  ],
  exports: [
    RouterModule
  ]
})
export class NLMModule { }
