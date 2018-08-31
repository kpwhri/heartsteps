import { Component, OnInit, Input } from '@angular/core';
import * as moment from 'moment';
import { ModalController } from 'ionic-angular';
import { PlanModal } from '@pages/activity-plan/plan.modal';

@Component({
    selector: 'activity-day-plan',
    templateUrl: './day-plan.component.html',
    inputs: ['date']
})
export class DayPlanComponent implements OnInit {

    @Input() date:Date
    dateFormatted:string

    plans: Array<any> = []

    constructor(
        private modalCtrl:ModalController
    ) {}

    ngOnInit(){
        this.dateFormatted = moment(this.date).format("dddd, M/D")
    }
    
    addPlan() {
        let modal = this.modalCtrl.create(PlanModal);

        modal.onDidDismiss((plan:any) => {
            if(plan) {
                this.plans.push(plan)
            }
        });

        modal.present()
    }
}
