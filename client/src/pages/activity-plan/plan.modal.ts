import { Component } from '@angular/core';
import { ViewController, NavParams } from 'ionic-angular';
import { ActivityPlanService } from '@heartsteps/activity-plan.service';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { Activity } from '@heartsteps/activity.model';

@Component({
    selector: 'activity-plan-modal',
    templateUrl: 'plan.modal.html'
})
export class PlanModal {
    private activity:Activity;
    
    public durationChoices: Array<number> = [
        5, 10, 15, 20, 25, 30, 
    ]
    public planForm:FormGroup;

    private updateView:boolean;
    public date:string;
    public error:string;
    

    constructor(
        params:NavParams,
        private viewCtrl:ViewController,
        private activityPlanService:ActivityPlanService,
    ) {
        if (params.get('activity')) {
           this.updateView = true;
           this.activity = new Activity(params.get('activity')); 
        } else {
            this.updateView = false;
            this.activity = new Activity({});
            this.activity.updateStartDate(params.get('date'));
        }

        this.date = this.activity.getStartDate();

        this.planForm = new FormGroup({
            activity: new FormControl(this.activity.type, Validators.required),
            duration: new FormControl(this.activity.duration, Validators.required),
            time: new FormControl(this.activity.getStartTime(), Validators.required),
            vigorous: new FormControl(this.activity.vigorous, Validators.required)
        });
    }

    dismiss() {
        this.viewCtrl.dismiss()
    }

    updateActivity() {
        this.activity.type = this.planForm.value.activity;
        this.activity.duration = this.planForm.value.duration;
        this.activity.vigorous = this.planForm.value.vigorous;
        this.activity.updateStartTime(this.planForm.value.time);
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