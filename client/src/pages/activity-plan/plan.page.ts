import { Component } from '@angular/core';
import { DateFactory } from '@infrastructure/date.factory';
import { ModalController } from 'ionic-angular';
import { PlanModal } from '@heartsteps/activity/plan.modal';
import { CurrentWeekService } from '@heartsteps/weekly-survey/current-week.service';

@Component({
    selector: 'page-plan',
    templateUrl: 'plan.page.html',
    providers: [DateFactory]
})
export class PlanPage {

    dates:Array<Date>

    constructor(
        private currentWeekService: CurrentWeekService,
        private modalCtrl:ModalController
    ) {
        this.currentWeekService.getDays().then((dates) => {
            this.dates = dates;
        })
    }

    addActivity(date:Date) {
        let modal = this.modalCtrl.create(PlanModal, {
            date: date
        });
        modal.present()
    }
}
