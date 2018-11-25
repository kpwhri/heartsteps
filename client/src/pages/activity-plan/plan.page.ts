import { Component } from '@angular/core';
import { DateFactory } from '@infrastructure/date.factory';
import { ModalController } from 'ionic-angular';
import { PlanModal } from '@pages/activity-plan/plan.modal';

@Component({
    selector: 'page-plan',
    templateUrl: 'plan.page.html',
    providers: [DateFactory]
})
export class PlanPage {

    dates:Array<Date>

    constructor(
        dateFactory:DateFactory,
        private modalCtrl:ModalController
    ) {
        this.dates = dateFactory.getCurrentWeek();
    }

    addActivity(date:Date) {
        let modal = this.modalCtrl.create(PlanModal, {
            date: date
        });
        modal.present()
    }
}
