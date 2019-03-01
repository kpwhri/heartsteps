import { Component, Output, EventEmitter } from '@angular/core';
import { FormControl, Validators, FormGroup } from '@angular/forms';

import { LoadingService } from '@infrastructure/loading.service';
import { ReflectionTimeService, ReflectionTime } from './reflection-time.service';
import { SelectOption } from '@infrastructure/dialogs/select-dialog.controller';

@Component({
  selector: 'weekly-reflection-time',
  templateUrl: 'weekly-reflection-time.page.html'
})
export class WeeklyReflectionTimePage {

    public weeklyReflectionForm: FormGroup;
    public days:Array<SelectOption> = [{
        'name': 'Saturday',
        'value': 'saturday'
    }, {
        'name': 'Sunday',
        'value': 'sunday'
    }];

    @Output() saved = new EventEmitter<boolean>();

    constructor(
        private loadingService:LoadingService,
        private reflectionTimeService:ReflectionTimeService
    ) {
        this.reflectionTimeService.getTime()
        .catch(() => {
            return this.reflectionTimeService.getDefaultReflectionTime()
        })
        .then((reflectionTime: ReflectionTime)=> {
            this.createReflectionForm(reflectionTime.day, reflectionTime.time);
        });
    }

    createReflectionForm(day: string, time: Date) {
        this.weeklyReflectionForm = new FormGroup({
            day: new FormControl(day, Validators.required),
            time: new FormControl(time, Validators.required)
        })
    }

    save() {
        if(this.weeklyReflectionForm.valid) {
            this.loadingService.show('Saving reflection time')
            this.reflectionTimeService.setTime(this.weeklyReflectionForm.value)
            .then(() => {
                this.saved.emit(true);                
            })
            .catch((error) => {

            })
            .then(() => {
                this.loadingService.dismiss()
            })
        }
    }
    

}
