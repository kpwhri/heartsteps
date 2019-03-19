import { Injectable } from "@angular/core";
import { Resolve, ActivatedRouteSnapshot } from "@angular/router";
import { ActivityPlanService } from "@heartsteps/activity-plans/activity-plan.service";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";



@Injectable()
export class ActivityPlanResolver implements Resolve<ActivityPlan> {
    
    constructor(
        private activityPlanService: ActivityPlanService
    ){}

    resolve(route: ActivatedRouteSnapshot) {
        return this.activityPlanService.get(route.paramMap.get('id'));
    }
}
