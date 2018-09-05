import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { FormControl, Validators, FormGroup } from '@angular/forms';

import { loadingService } from '../../infrastructure/loading.service';
import { ReflectionTimeService } from '@heartsteps/reflection-time.service';

@Component({
  selector: 'page-weekly-reflection-time',
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

    constructor(
        private navCtrl:NavController,
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
                this.navCtrl.pop()
            })
            .catch(() => {

            })
            .then(() => {
                this.loadingService.dismiss()
            })
        }
    }
    

}
