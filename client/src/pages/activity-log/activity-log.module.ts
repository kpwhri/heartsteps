import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ActivityLogPage } from './activity-log';
import { LogModal } from '@pages/activity-log/log.modal';

@NgModule({
  declarations: [
    ActivityLogPage,
    LogModal
  ],
  entryComponents: [
    LogModal
  ],
  imports: [
    IonicPageModule.forChild(ActivityLogPage),
  ],
})
export class ActivityLogModule {}
