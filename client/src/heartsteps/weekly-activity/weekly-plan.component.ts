import { Component, Input } from '@angular/core';
import { DateFactory } from '@infrastructure/date.factory';
import { ModalController } from 'ionic-angular';
import { PlanModal } from '@heartsteps/activity/plan.modal';
import { Week } from '@heartsteps/weekly-survey/week.model';

@Component({
    selector: 'heartsteps-weekly-plan',
    templateUrl: 'weekly-plan.component.html',
    providers: [DateFactory],
    inputs: ['week']
})
export class WeeklyPlanComponent {

    private _week: Week;
    dates:Array<Date>

    constructor(
        private modalCtrl:ModalController
    ) {}

    @Input()
    set week(week:Week) {
        if(week) {
            this._week = week;
            this.dates = week.getDays();
        }
    }

    addActivity(date:Date) {
        let modal = this.modalCtrl.create(PlanModal, {
            date: date
        });
        modal.present()
    }
}
