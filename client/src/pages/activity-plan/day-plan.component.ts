import { Component, Input, OnDestroy } from '@angular/core';
import { ActivityPlanService } from '@heartsteps/activity-plans/activity-plan.service';
import { Subscription } from 'rxjs';
import * as moment from 'moment';
import { Router } from '@angular/router';
import { DateFactory } from '@infrastructure/date.factory';

@Component({
    selector: 'activity-plan-day',
    templateUrl: './day-plan.component.html'})
export class DayPlanComponent implements OnDestroy {

    public title: string;
    public date: Date;

    public isToday: boolean;
    public hideIsToday: boolean;
    
    public canAddActivity:boolean = false;
    public plans: Array<any>;

    private activityPlanSubscription: Subscription;

    constructor(
        private activityPlanService:ActivityPlanService,
        private router: Router,
        private dateFactory: DateFactory
    ) {}

    ngOnDestroy() {
        if(this.activityPlanSubscription) {
            this.activityPlanSubscription.unsubscribe();
        }
    }

    @Input('label')
    set setLabel(label: string) {
        if(label) {
            this.title = label;
            this.hideIsToday = true;
            this.update();
        }
    }

    @Input('date')
    set updateDate(date:Date) {
        if(date) {
            this.date = date;
            this.isToday = this.dateFactory.isSameDay(date, new Date());
            this.update();
        }
    }

    private update() {
        if (!this.title) {
            this.title = moment(this.date).format("dddd, M/D");
        }
        this.getPlans();
        this.updateCanCreate();
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
        this.router.navigate([{
            outlets: {
                modal: 'plans/create/' + this.dateFactory.formatDate(this.date) 
            }
        }]);
    }
}
