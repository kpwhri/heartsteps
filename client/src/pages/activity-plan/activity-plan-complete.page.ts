import { Component } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";


@Component({
    templateUrl: './activity-plan-complete.page.html'
})
export class ActivityPlanCompletePage {

    public plan:ActivityPlan

    constructor(
        activatedRoute: ActivatedRoute,
        private router: Router
    ){
        this.plan = activatedRoute.snapshot.data['activityPlan'];
    }

    public editPlan() {
        this.router.navigate(['plans/edit', this.plan.id]);
    }

    public dismiss() {
        this.router.navigate(['/']);
    }

}
