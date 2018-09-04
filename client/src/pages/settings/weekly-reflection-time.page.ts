import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { FormControl, Validators, FormGroup } from '@angular/forms';

import { loadingService } from '../../infrastructure/loading.service';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';

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
        private heartstepsServer:HeartstepsServer
    ) {
        this.weeklyReflectionForm = new FormGroup({
            day: new FormControl('sunday', Validators.required),
            time: new FormControl('20:00', Validators.required)
        })
    }

    save() {
        if(this.weeklyReflectionForm.valid) {
            this.loadingService.show('Saving reflection time')
            this.heartstepsServer.post('reflection-time', this.weeklyReflectionForm.value)
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
