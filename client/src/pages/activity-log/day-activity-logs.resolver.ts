import { Injectable } from "@angular/core";
import { Resolve, ActivatedRouteSnapshot } from "@angular/router";import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { ActivityLogService } from "@heartsteps/activity-logs/activity-log.service";
import * as moment from 'moment';

@Injectable()
export class DayActivityLogsResolver implements Resolve<Array<ActivityLog>> {

    constructor(
        private activityLogService:ActivityLogService
    ){}

    resolve(route:ActivatedRouteSnapshot) {
        const date: Date = moment(route.paramMap.get('date'), 'YYYY-MM-DD').toDate();
        return this.activityLogService.getDate(date);
    }
}
