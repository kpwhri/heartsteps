import { Component } from "@angular/core";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";
import { ActivatedRoute } from "@angular/router";
import { DateFactory } from "@infrastructure/date.factory";
import { Location } from "@angular/common";



@Component({
    templateUrl: './create-plan.page.html'
})
export class CreatePlanPage {

    public plan:ActivityPlan; 
    public date:Date;

    constructor(
        private dateFactory: DateFactory,
        private location: Location,
        activatedRoute: ActivatedRoute
    ) {
        activatedRoute.data.subscribe((data) => {
            if(data && data['date']) {
                this.date = this.dateFactory.parseDate(activatedRoute.snapshot.data['date']);
                this.plan.updateStartDate(this.date);
            }
        })

        this.plan = new ActivityPlan();
    }

    public back() {
        this.location.back();
    }
}
