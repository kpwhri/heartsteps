import { Component } from '@angular/core';
import { IonicPage } from 'ionic-angular';
import { ActivityPlanService } from '@heartsteps/activity-plan.service';
import { DayPlanComponent } from '@pages/activity-plan/day-plan.component';


@IonicPage()
@Component({
    selector: 'page-plan',
    templateUrl: 'plan.html',
    entryComponents: [DayPlanComponent]
})
export class PlanPage {

    dates:Array<Date>

    constructor(
        private activityPlanService:ActivityPlanService
    ) {

    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad PlanPage');
        this.dates = this.activityPlanService.getCurrentWeek()
    }

}
