import { Component } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";
import { FormGroup } from "@angular/forms";


@Component({
    templateUrl: './activity-plan-complete.page.html'
})
export class ActivityPlanCompletePage {

    public plan:ActivityPlan;
    public form:FormGroup;

    constructor(
        activatedRoute: ActivatedRoute,
        private router: Router
    ){
        this.plan = activatedRoute.snapshot.data['activityPlan'];
        this.form = new FormGroup({});
    }

    public editPlan() {
        this.router.navigate(['plans', this.plan.id]);
    }

    public dismiss() {
        this.router.navigate(['/']);
    }

}
