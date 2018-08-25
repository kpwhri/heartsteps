import { Component } from '@angular/core';
import { IonicPage } from 'ionic-angular';
import { ActivityPlanFactory } from '@heartsteps/activity-plan/activity-plan.factory';

@IonicPage()
@Component({
    selector: 'page-plan',
    templateUrl: 'plan.html'
})
export class PlanPage {

    dates:Array<Date>

    constructor(
        private activityPlanFactory:ActivityPlanFactory
    ) {

    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad PlanPage');
        this.dates = this.activityPlanFactory.getCurrentWeek()
    }

}
