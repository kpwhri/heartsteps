import { Component, Input, OnDestroy, Output, EventEmitter } from '@angular/core';
import { ActivityPlanService } from '@heartsteps/activity-plans/activity-plan.service';
import { Subscription } from 'rxjs';
import { ActivityPlan } from '@heartsteps/activity-plans/activity-plan.model';
import * as moment from 'moment';
import { Router } from '@angular/router';

@Component({
    selector: 'activity-plan-day',
    templateUrl: './day-plan.component.html'})
export class DayPlanComponent implements OnDestroy {

    public date: Date;
    public canAddActivity:boolean = false;
    public plans: Array<any>;

    private activityPlanSubscription: Subscription;

    constructor(
        private activityPlanService:ActivityPlanService,
        private router: Router
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
            this.updateCanCreate();
        }
    }

    private updateCanCreate() {
        if(this.date >= new Date() || moment().isSame(this.date, 'day')) {
            this.canAddActivity = true;
        } else {
            this.canAddActivity = false;
        }
    }

    private getPlans() {
        this.activityPlanSubscription = this.activityPlanService.getPlansOn(this.date)
        .subscribe((plans) => {
            this.plans = plans;
        });
    }

    public createPlan() {
        this.router.navigate(['plans/create', this.date]);
    }

    public showPlan(plan:ActivityPlan) {
        this.router.navigate(['plans/complete', plan.id]);
    }
}
