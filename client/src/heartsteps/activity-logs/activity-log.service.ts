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

    public getLog(logId:string):Promise<ActivityLog> {
        return this.heartstepsServer.get('activity/logs/' + logId)
        .then((data) => {
            return this.deserializeActivityLog(data);
        });
    }

    public save(activityLog:ActivityLog):Promise<ActivityLog> {
        return this.heartstepsServer.post(
            'activity/logs/' + activityLog.id,
            this.serialize(activityLog)    
        )
        .then((data) => {
            return this.deserializeActivityLog(data);
        });
    }

    public delete(activityLog:ActivityLog):Promise<boolean> {
        return this.heartstepsServer.delete('activity/logs/' + activityLog.id)
        .then(() => {
            return true;
        });
    }

    private serialize(activityLog):any {
        return {
            id: activityLog.id,
            start: activityLog.start,
            duration: activityLog.duration,
            type: activityLog.type,
            vigorous: activityLog.vigorous
        }
    }

    private deserializeActivityLog(data:any):ActivityLog {
        const activityLog:ActivityLog = new ActivityLog();
        activityLog.id = data.id;
        activityLog.start = moment(data.start).toDate();
        activityLog.type = data.type;
        activityLog.duration = data.duration;
        activityLog.earnedMinutes = data.earnedMinutes;
        activityLog.vigorous = data.vigorous;
        return activityLog;
    }

}
