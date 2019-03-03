import { Component } from "@angular/core";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";
import { ActivatedRoute } from "@angular/router";
import { DateFactory } from "@infrastructure/date.factory";
import { Location } from "@angular/common";
import { FormGroup, FormControl } from "@angular/forms";
import { ActivityPlanService } from "@heartsteps/activity-plans/activity-plan.service";
import { LoadingService } from "@infrastructure/loading.service";



@Component({
    templateUrl: './create-plan.page.html'
})
export class CreatePlanPage {

    public planForm: FormGroup;
    public date:Date;

    constructor(
        private activityPlanService: ActivityPlanService,
        private dateFactory: DateFactory,
        private location: Location,
        private loadingService: LoadingService,
        activatedRoute: ActivatedRoute
    ) {


        const plan = new ActivityPlan();
        this.planForm = new FormGroup({
            activityPlan: new FormControl(plan)
        });
    }

    public create() {
        this.loadingService.show('Saving activity plan');
        const activityPlan = this.planForm.value.activityPlan;
        this.activityPlanService.save(activityPlan)
        .then(() => {
            this.back();
        })
        .catch((error) => {
            console.log(error);
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public back() {
        this.location.back();
    }
}
