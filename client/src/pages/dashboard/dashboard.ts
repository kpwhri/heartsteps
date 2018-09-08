import { Component } from '@angular/core';
import { IonicPage, ModalController } from 'ionic-angular';
import { DateFactory } from '@heartsteps/date.factory';
import { ActivityLogService } from '@heartsteps/activity-log.service';
import { LogModal } from '@pages/activity-log/log.modal';

@IonicPage()
@Component({
    selector: 'page-dashboard',
    templateUrl: 'dashboard.html',
    entryComponents: [LogModal]
})
export class DashboardPage {

    private remainingPlans: Array<any>
    private dates: Array<Date>

    constructor(
        dateFactory: DateFactory,
        private activityLogService:ActivityLogService,
        private modalCtrl: ModalController
    ) {
        this.dates = dateFactory.getRemainingDaysInWeek()
    }

    logActivity() {
        let modal = this.modalCtrl.create(LogModal);
        modal.present();
    }
}
