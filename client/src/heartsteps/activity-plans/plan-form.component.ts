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
    public availableDates:Array<string>

    public planForm:FormGroup;
    public error:string;

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

    save() {
        if (this.planForm.valid) {
            this.updateActivity();
            this.activityPlanService.save(this.activityPlan)
            .then(() => {
                this.saved.emit();
            })
            .catch((error) => {
                if(error.message) {
                    this.error = error.message;
                }
            })
        }
    }

    complete() {
        if(this.planForm.valid) {
            this.updateActivity();
            this.activityPlanService.complete(this.activityPlan)
            .then(() => {
                this.saved.emit();
            })
        }
    }

    delete() {
        this.activityPlanService.delete(this.activityPlan)
        .then(() => {
            this.saved.emit();
        });
    }

}