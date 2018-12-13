import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import {BehaviorSubject} from 'rxjs';
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Activity } from "@heartsteps/activity/activity.model";
import { ActivityLog } from './activity-log.model';

@Injectable()
export class ActivityLogService {

    constructor(
        private heartstepsServer:HeartstepsServer
    ){}

    get(date:Date):Promise<Array<ActivityLog>> {
        return this.heartstepsServer.get('activity/logs/' + moment(date).format('YYYY-MM-DD'))
        .then((logs:Array<any>) => {
            const activityLogs:Array<ActivityLog> = [];
            logs.forEach((log:any) => {
                activityLogs.push(
                    this.deserializeActivityLog(log)
                );
            })
            return activityLogs;
        });
    }

    private deserializeActivityLog(log:any):ActivityLog {
        const activityLog:ActivityLog = new ActivityLog();
        activityLog.id = log.id;
        activityLog.type = log.type;
        activityLog.vigorousMinutes = log.vigorous_minutes;
        activityLog.moderateMinutes = log.moderate_minutes;
        activityLog.totalMinutes = log.total_minutes;

        activityLog.start = moment(log.start).toDate();
        activityLog.end = moment(log.end).toDate();

        return activityLog;
    }

}
