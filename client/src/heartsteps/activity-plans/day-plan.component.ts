import { Component, Input, OnDestroy } from '@angular/core';
import { ActivityPlanService } from './activity-plan.service';
import { Subscription } from 'rxjs';
import { PlanModalController } from './plan-modal.controller';
import { ActivityPlan } from './activity-plan.model';
import * as moment from 'moment';

@Component({
    selector: 'activity-plan-day',
    templateUrl: './day-plan.component.html',
    inputs: ['date'],
    providers: [PlanModalController]
})
export class DayPlanComponent implements OnDestroy {

    public date: Date;
    public canAddActivity:boolean = false;
    public plans: Array<any>;

    private activityPlanSubscription: Subscription;

    constructor(
        private activityPlanService:ActivityPlanService,
        private planModal:PlanModalController
    ) {}

    ngOnDestroy() {
        if(this.activityPlanSubscription) {
            this.activityPlanSubscription.unsubscribe();
        }
    }

    @Input('date')
    set updateDate(date:Date) {
        if(date) {
            this.date = date;
            this.getPlans();
            if(date >= new Date() || moment().isSame(date, 'day')) {
                this.canAddActivity = true;
            } else {
                this.canAddActivity = false;
            }
        }
    }

    getPlans() {
        this.activityPlanSubscription = this.activityPlanService.getPlansOn(this.date)
        .subscribe((plans) => {
            if(plans && plans.length) {
                this.plans = plans;
            } else {
                this.plans = null;
            }
        })
    }

    addActivity() {
        const plan = new ActivityPlan();
        plan.updateStartDate(this.date);
        this.planModal.show(plan);
    }

    showPlan(plan:ActivityPlan) {
        this.planModal.show(plan);
    }

    filterPlans(plans) {
        const filteredPlans = [];
        if(plans && plans.length > 0) {
            plans.forEach((plan) => {

            });
        }
        if (filteredPlans.length > 0) {
            this.plans = filteredPlans;
        } else {
            this.plans = null;
        }
    }
}
