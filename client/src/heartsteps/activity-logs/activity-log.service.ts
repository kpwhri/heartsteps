import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { ActivityLog } from './activity-log.model';

@Injectable()
export class ActivityLogService {

    constructor(
        private heartstepsServer:HeartstepsServer
    ){}

    getDate(date:Date):Promise<Array<ActivityLog>> {
        const start:Date = new Date(date.valueOf());
        start.setHours(0, 0);
        const end:Date = new Date(date.valueOf());
        end.setHours(23, 59);
        return this.get(start, end);
    }

    get(start:Date, end:Date):Promise<Array<ActivityLog>> {
        return this.heartstepsServer.get('activity/logs/', {
            start: start.toISOString(),
            end: end.toISOString()
        })
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
