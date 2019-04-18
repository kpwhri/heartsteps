import { Component } from "@angular/core";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";
import { ActivatedRoute, Router } from "@angular/router";
import { DateFactory } from "@infrastructure/date.factory";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { ActivityPlanService } from "@heartsteps/activity-plans/activity-plan.service";
import { LoadingService } from "@infrastructure/loading.service";



@Component({
    templateUrl: './create-plan.page.html'
})
export class CreatePlanPage {

    public planForm: FormGroup;
    public date:Date;
    public error: string;

    constructor(
        private activityPlanService: ActivityPlanService,
        private dateFactory: DateFactory,
        private router: Router,
        private loadingService: LoadingService,
        activatedRoute: ActivatedRoute
    ) {
        const dateStr:string = activatedRoute.snapshot.paramMap.get('date');
        const date = this.dateFactory.parseDate(dateStr);

        const plan = new ActivityPlan();
        plan.date = date;

        this.planForm = new FormGroup({
            activityPlan: new FormControl(plan, Validators.required)
        });
    }

    public create() {
        this.error = undefined;
        this.loadingService.show('Saving activity plan');
        const activityPlan = this.planForm.value.activityPlan;
        this.activityPlanService.save(activityPlan)
        .then(() => {
            this.back();
        })
        .catch((error) => {
            this.error = error;
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public back() {
        this.router.navigate([{outlets:{modal:null}}]);
    }
}
