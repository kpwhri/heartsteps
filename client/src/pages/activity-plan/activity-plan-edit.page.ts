import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";

@Component({
    templateUrl: './activity-plan-edit.page.html'
})
export class ActivityPlanEditPage implements OnInit {

    public activityPlan: ActivityPlan;

    constructor(
        private activatedRoute: ActivatedRoute,
        private router: Router
    ){}

    public ngOnInit() {
        this.activityPlan = this.activatedRoute.snapshot.data['activityPlan'];
    }

    public complete() {
        this.router.navigate(['plans', 'complete', this.activityPlan.id]);
    }

    public dismiss() {
        this.router.navigate(['/']);
    }

}
