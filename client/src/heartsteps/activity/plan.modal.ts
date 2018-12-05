import * as moment from 'moment';

import { Component } from '@angular/core';
import { ViewController, NavParams } from 'ionic-angular';
import { FormGroup, FormControl, Validators } from '@angular/forms';

import { ActivityPlanService } from './activity-plan.service';
import { Activity } from './activity.model';
import { DateFactory } from '@infrastructure/date.factory';

@Component({
    selector: 'activity-plan-modal',
    templateUrl: 'plan.modal.html',
    providers: [
        DateFactory
    ]
})
export class PlanModal {
    private activity:Activity;
    
    public planForm:FormGroup;
    public availableDates:Array<string>

    public updateView:boolean;
    public error:string;
    

    constructor(
        params:NavParams,
        private viewCtrl:ViewController,
        private activityPlanService:ActivityPlanService,
        private dateFactory: DateFactory
    ) {

        let defaultDate:string;
        let defaultTime:string;

        if (params.get('activity')) {
           this.updateView = true;
           this.activity = new Activity(params.get('activity')); 
           defaultTime = this.activity.getStartTime();
           defaultDate = this.activity.getStartDate();
        } else {
            this.updateView = false;
            this.activity = new Activity({});
            defaultDate = this.formatDate(params.get('date'));
        }

        this.availableDates = [];
        this.dateFactory.getRemainingDaysInWeek().forEach((date:Date) => {
            this.availableDates.push(this.formatDate(date));
        });

        this.planForm = new FormGroup({
            activity: new FormControl(this.activity.type, Validators.required),
            duration: new FormControl(this.activity.duration, Validators.required),
            date: new FormControl(defaultDate, Validators.required),
            time: new FormControl(defaultTime, Validators.required),
            vigorous: new FormControl(this.activity.vigorous, Validators.required)
        });
    }

    dismiss() {
        this.viewCtrl.dismiss()
    }

    formatDate(date:Date):string {
        return moment(date).format('dddd, M/D');
    }

    parseDate(str:string):Date {
        return moment(str, 'dddd, M/D').toDate();
    }

    updateActivity() {
        this.activity.type = this.planForm.value.activity;
        this.activity.duration = this.planForm.value.duration;
        this.activity.vigorous = this.planForm.value.vigorous;
        this.activity.updateStartTime(this.planForm.value.time);
        this.activity.updateStartDate(this.parseDate(this.planForm.value.date));
    }

    save() {
        if (this.planForm.valid) {
            this.updateActivity();
            this.activityPlanService.createPlan(this.activity)
            .then((plan) => {
                this.viewCtrl.dismiss(plan)
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
            this.activityPlanService.complete(this.activity)
            .then((activity: Activity) => {
                this.viewCtrl.dismiss(activity);
            })
        }
    }

}