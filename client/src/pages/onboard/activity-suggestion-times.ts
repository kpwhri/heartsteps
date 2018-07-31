import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { HeartstepsServer } from '../../infrastructure/heartsteps-server.service';
import { loadingService } from '../../infrastructure/loading.service';

@Component({
  selector: 'activity-suggestion-times',
  templateUrl: 'activity-suggestion-times.html',
})
export class ActivitySuggestionTimes {

    private entryTimes:Array<any>;
    private times:any;

    constructor(
        private navCtrl:NavController,
        private heartstepsServer:HeartstepsServer,
        private loadingService:loadingService
    ) {}

    ionViewWillEnter() {
        return this.getTimes();
    }

    getTimes():Promise<boolean> {
        this.entryTimes = [
            { key:'morning', name:'Morning'},
            { key:'lunch', name:'Lunch'},
            { key:'midafternoon', name:'Afternoon'},
            { key:'evening', name:'Evening'},
            { key:'postdinner', name:'Post Dinner'}
        ]
        this.times = {}
        return Promise.resolve(true);
    }

    updateTimes() {
        this.loadingService.show('Saving activity suggestion schedule')
        this.heartstepsServer.post(
            'activity-suggestions/times',
            this.times
        )
        .then(() => {
            this.loadingService.dismiss()
            this.navCtrl.pop();
        });
    }
}
