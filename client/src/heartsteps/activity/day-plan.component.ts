import { Component, OnInit, Input, OnDestroy } from '@angular/core';
import * as moment from 'moment';
import { ActivityPlanService } from '@heartsteps/activity/activity-plan.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'activity-plan-day',
    templateUrl: './day-plan.component.html',
    inputs: ['date']
})
export class DayPlanComponent implements OnInit, OnDestroy {

    @Input() date: Date;
    plans: Array<any>;

    activityPlanSubscription: Subscription;

    constructor(
        private activityPlanService:ActivityPlanService
    ) {}

    ngOnInit(){
        this.activityPlanSubscription = this.activityPlanService.plans.subscribe((plans) => {
            this.filterPlans(plans);
        });
    }

    ngOnDestroy() {
        this.activityPlanSubscription.unsubscribe();
    }

    filterPlans(plans) {
        const filteredPlans = [];
        if(plans && plans.length > 0) {
            plans.forEach((plan) => {
                if(moment(this.date).format("YYYY-MM-DD") == moment(plan.start).format("YYYY-MM-DD")) {
                    filteredPlans.push(plan);
                }
            });
        }
        if (filteredPlans.length > 0) {
            this.plans = filteredPlans;
        } else {
            this.plans = null;
        }
    }
}
