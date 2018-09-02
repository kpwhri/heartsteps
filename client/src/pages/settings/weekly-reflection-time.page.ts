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

    constructor(
        private navCtrl:NavController,
        private loadingService:loadingService,
        private heartstepsServer:HeartstepsServer
    ) {}


}
