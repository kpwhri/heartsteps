import { Component, Output, EventEmitter, OnInit } from '@angular/core';
import { FormControl, Validators, FormGroup } from '@angular/forms';

import { LoadingService } from '@infrastructure/loading.service';
import { WalkingSuggestionTimeService } from './walking-suggestion-time.service';

@Component({
  selector: 'heartsteps-walking-suggestion-times',
  templateUrl: './walking-suggestion-times.component.html'
})
export class WalkingSuggestionTimesComponent implements OnInit {
    @Output() saved = new EventEmitter<boolean>();

    public timeFields:Array<any> = [];
    public times:any;

    public timesForm:FormGroup = new FormGroup({});

    constructor(
        private activitySuggestionTimeService:WalkingSuggestionTimeService,
        private loadingService:LoadingService
    ) {}

    ngOnInit() {
        return this.activitySuggestionTimeService.getTimes()
        .catch(() => {
            return {}
        })
        .then((times) => {
            this.times = times;
        })
        .then(() => {
            return this.activitySuggestionTimeService.getTimeFields();
        })
        .then((timeFields) => {
            this.timeFields = timeFields;
            let controls = {}
            this.timeFields.forEach((timeField) => {
                controls[timeField.key] = new FormControl(this.times[timeField.key], Validators.required)
            });
            this.timesForm = new FormGroup(controls)
        });
    }

    public updateTimes() {
        this.loadingService.show('Saving activity suggestion schedule')
        this.activitySuggestionTimeService.updateTimes(this.timesForm.value)
        .then(() => {
            this.saved.emit(true);
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
