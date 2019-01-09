import { Injectable } from "@angular/core";
import { Resolve, ActivatedRouteSnapshot } from "@angular/router";import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { ActivityLogService } from "@heartsteps/activity-logs/activity-log.service";


@Injectable()
export class ActivityLogResolver implements Resolve<ActivityLog> {

    constructor(
        private activityLogService:ActivityLogService
    ){}

    resolve(route:ActivatedRouteSnapshot) {
        return this.activityLogService.getLog(route.paramMap.get('id'));
    }
}
