import { Component, Output, EventEmitter } from '@angular/core';
import { FormControl, Validators, FormGroup } from '@angular/forms';

import { loadingService } from '@infrastructure/loading.service';
import { ReflectionTimeService } from './reflection-time.service';

@Component({
  selector: 'weekly-reflection-time',
  templateUrl: 'weekly-reflection-time.page.html'
})
export class WeeklyReflectionTimePage {

    days:Array<string> = [
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday'
    ]
    weeklyReflectionForm: FormGroup;
    @Output() saved = new EventEmitter<boolean>();

    constructor(
        private loadingService:loadingService,
        private reflectionTimeService:ReflectionTimeService
    ) {
        this.reflectionTimeService.getTime()
        .then((data: any)=> {
            this.createReflectionForm(data.day, data.time);
        })
        .catch(() => {
            this.createReflectionForm('sunday', '20:00');
        })
    }

    createReflectionForm(day: string, time: string) {
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
            .then(() => {
                this.loadingService.dismiss()
            })
        }
    }
    

}
