import { Injectable } from "@angular/core";
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router, Resolve } from "@angular/router";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";
import { ActivityPlanService } from "@heartsteps/activity-plans/activity-plan.service";


@Injectable()
export class CompletePlanGaurd implements CanActivate {

    constructor(
        private router: Router
    ) {}

    canActivate(next:ActivatedRouteSnapshot, state: RouterStateSnapshot):boolean {
        const plan:ActivityPlan = next.data['activityPlan'];
        if(plan.isComplete()) {
            this.router.navigate(['plans', plan.id]);
            return false;
        } else {
            return true;
        }
    }

}

@Injectable()
export class CompletePlanResolver implements Resolve<ActivityPlan> {

    constructor(
        private activityPlanService: ActivityPlanService,
        private router: Router
    ){}

    resolve(route: ActivatedRouteSnapshot) {
        return this.activityPlanService.get(route.paramMap.get('id'))
        .then((activityPlan) => {
            if(activityPlan.isComplete()) {
                this.router.navigate(['plans', activityPlan.id]);
                return Promise.reject('Plan is already complete');
            } else {
                return Promise.resolve(activityPlan);
            }
        });
    }

}
