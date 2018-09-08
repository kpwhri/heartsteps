import { Component } from '@angular/core';
import { ViewController, NavParams } from 'ionic-angular';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { Activity } from '@heartsteps/activity.model';
import { ActivityLogService } from '@heartsteps/activity-log.service';

@Component({
    selector: 'activity-log-modal',
    templateUrl: 'log.modal.html'
})
export class LogModal {
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
        private activityLogService: ActivityLogService
    ) {
        if (params.get('activity')) {
           this.updateView = true;
           this.activity = new Activity(params.get('activity')); 
        } else {
            this.updateView = false;
            this.activity = new Activity({});
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
            this.activityLogService.create(this.activity)
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
}