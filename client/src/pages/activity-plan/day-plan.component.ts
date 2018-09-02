import { Component, OnInit, Input } from '@angular/core';
import * as moment from 'moment';
import { PlanModal } from '@pages/activity-plan/plan.modal';
import { ActivityPlanService } from '@heartsteps/activity-plan.service';

@Component({
    selector: 'activity-plan-day',
    templateUrl: './day-plan.component.html',
    inputs: ['date']
})
export class DayPlanComponent implements OnInit {

    @Input() date:Date
    dateFormatted:string

    plans: Array<any> = []

    constructor(
        private activityPlanService:ActivityPlanService
    ) {}

    ngOnInit(){
        this.dateFormatted = moment(this.date).format("dddd, M/D")
        this.activityPlanService.getPlansForDate(this.date)
        .then((plans) => {
            this.plans = plans
        })
    }
}
