import * as moment from 'moment';

import { Component, Input, OnInit, Output, EventEmitter } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';

import { ActivityPlanService } from './activity-plan.service';
import { ActivityPlan } from './activity-plan.model';
import { DateFactory } from '@infrastructure/date.factory';

@Component({
    selector: 'activity-plan-form',
    templateUrl: './plan-form.component.html',
    providers: [
        DateFactory
    ],
    inputs: ['plan']
})
export class PlanFormComponent implements OnInit {

    @Output() saved = new EventEmitter<boolean>();

    public activityPlan:ActivityPlan;
    public availableDates:Array<string>;

    public planForm:FormGroup;
    public error:string;

    public updateView:boolean;

    constructor(
        private activityPlanService:ActivityPlanService,
        private dateFactory: DateFactory
    ) {}

    ngOnInit() {
        this.availableDates = [];
        this.dateFactory.getRemainingDaysInWeek().forEach((date:Date) => {
            this.availableDates.push(this.formatDate(date));
        });
    }

    @Input('plan')
    set plan(activityPlan:ActivityPlan) {
        if(activityPlan) {
            this.activityPlan = activityPlan;
            this.planForm = new FormGroup({
                activity: new FormControl(this.activityPlan.type, Validators.required),
                duration: new FormControl(this.activityPlan.duration, Validators.required),
                date: new FormControl(this.activityPlan.getStartDate(), Validators.required),
                time: new FormControl(this.activityPlan.getStartTime(), Validators.required),
                vigorous: new FormControl(this.activityPlan.vigorous, Validators.required)
            });
            
            if(activityPlan.complete) {
                this.planForm.disable();
            }

            if(activityPlan.id) {
                this.updateView = true;
            } else {
                this.updateView = false;
            }
        }
    }

    formatDate(date:Date):string {
        return moment(date).format('dddd, M/D');
    }

    parseDate(str:string):Date {
        return moment(str, 'dddd, M/D').toDate();
    }

    updateActivity() {
        this.activityPlan.type = this.planForm.value.activity;
        this.activityPlan.duration = this.planForm.value.duration;
        this.activityPlan.vigorous = this.planForm.value.vigorous;
        this.activityPlan.updateStartTime(this.planForm.value.time);
        this.activityPlan.updateStartDate(this.parseDate(this.planForm.value.date));
    }

    validateActivity():Promise<ActivityPlan> {
        if(this.planForm.valid) {
            this.updateActivity();
            return Promise.resolve(this.activityPlan);
        } else {
            return Promise.reject("Invalid form");
        }
    }

    save() {
        this.validateActivity()
        .then((activityPlan) => {
            return this.activityPlanService.save(activityPlan);
        })
        .then(() => {
            this.saved.emit();
        })
        .catch((error) => {
            this.error = error;
        });
    }

    complete() {
        this.validateActivity()
        .then((activityPlan) => {
            return this.activityPlanService.complete(activityPlan);
        })
        .then(() => {
            this.saved.emit();
        });
    }

    uncomplete() {
        this.activityPlanService.uncomplete(this.activityPlan)
        .then(() => {
            this.saved.emit();
        });
    }

    delete() {
        this.activityPlanService.delete(this.activityPlan)
        .then(() => {
            this.saved.emit();
        });
    }

}