import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { FormControl, Validators, FormGroup, ValidationErrors, ValidatorFn } from '@angular/forms';

import { loadingService } from '../../infrastructure/loading.service';
import { ActivitySuggestionTimeService } from '../../heartsteps/activity-suggestion-time.service';

@Component({
  selector: 'activity-suggestion-times',
  templateUrl: 'activity-suggestion-times.html',
  providers: [
      ActivitySuggestionTimeService
  ]
})
export class ActivitySuggestionTimes {

    public timeFields:Array<any>;
    public times:any;

    public timesForm:FormGroup

    constructor(
        private navCtrl:NavController,
        private activitySuggestionTimeService:ActivitySuggestionTimeService,
        private loadingService:loadingService
    ) {}

    ionViewWillEnter() {
        return this.loadData()
        .then(() => {
            let controls = {}
            Object.keys(this.times).forEach((key) => {
                controls[key] = new FormControl(this.times[key], Validators.required)
            })
            this.timesForm = new FormGroup(controls)
        });
    }

    loadData():Promise<boolean> {
        this.times = {}
        return this.activitySuggestionTimeService.getTimeFields()
        .then((timeFields) => {
            this.timeFields = timeFields
            return this.activitySuggestionTimeService.getTimes()
        })
        .catch(() => {
            return this.activitySuggestionTimeService.getDefaultTimes()
        })
        .then((times) => {
            this.times = times
            return Promise.resolve(true)
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    updateTimes() {
        this.loadingService.show('Saving activity suggestion schedule')
        this.activitySuggestionTimeService.updateTimes(this.timesForm.value)
        .then(() => {
            this.navCtrl.pop();
        })
        .catch((errors) => {
            if(errors.outOfOrder) {
                errors.outOfOrder.forEach((key) => {
                    this.timesForm.get(key).setErrors({outOfOrder:true})
                })
            }
            if(errors.tooClose) {
                errors.tooClose.forEach((key) => {
                    this.timesForm.get(key).setErrors({tooClose:true})
                })
            }
        })
        .then(() => {
            this.loadingService.dismiss()
        })
    }
}
