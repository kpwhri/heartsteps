import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
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

    constructor(
        private navCtrl:NavController,
        private activitySuggestionTimeService:ActivitySuggestionTimeService,
        private loadingService:loadingService
    ) {}

    ionViewWillEnter() {
        return this.setup();
    }

    setup():Promise<boolean> {
        this.times = {}
        return this.activitySuggestionTimeService.getTimeFields()
        .then((timeFields) => {
            this.timeFields = timeFields
            return this.activitySuggestionTimeService.getTimes()
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
        this.activitySuggestionTimeService.updateTimes(this.times)
        .then(() => {
            this.loadingService.dismiss()
            this.navCtrl.pop();
        })
    }
}
