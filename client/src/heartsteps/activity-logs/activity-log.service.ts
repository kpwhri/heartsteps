import * as moment from 'moment';

import { Injectable, EventEmitter } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { ActivityLog } from './activity-log.model';

@Injectable()
export class ActivityLogService {

    public updated: EventEmitter<ActivityLog> = new EventEmitter();
    public deleted: EventEmitter<ActivityLog> = new EventEmitter();

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
        return this.heartstepsServer.get('activity/logs', {
            start: start.toISOString(),
            end: end.toISOString()
        })
        .then((logs:Array<any>) => {
            return logs.map((log) => {
                return this.deserialize(log);
            });
        })
        .then((logs:Array<ActivityLog>) => {
            this.sort(logs);
            return logs;
        });
    }

    public getLog(logId:string):Promise<ActivityLog> {
        return this.heartstepsServer.get('activity/logs/' + logId)
        .then((data) => {
            return this.deserialize(data);
        });
    }

    public save(activityLog:ActivityLog):Promise<ActivityLog> {
        let uri = 'activity/logs'
        if(activityLog.id) {
            uri = 'activity/logs/' + activityLog.id;
        }
        return this.heartstepsServer.post(uri,this.serialize(activityLog))
        .then((data) => {
            return this.deserialize(data);
        })
        .then((activityLog: ActivityLog) => {
            this.updated.emit(activityLog);
            return activityLog;
        });
    }

    public delete(activityLog:ActivityLog):Promise<boolean> {
        return this.heartstepsServer.delete('activity/logs/' + activityLog.id)
        .then(() => {
            this.deleted.emit(activityLog);
            return true;
        });
    }

    public serialize(activityLog):any {

        let vigorous: boolean = false;
        if(activityLog.vigorous) {
            vigorous = true;
        }

        return {
            id: activityLog.id,
            start: activityLog.start,
            duration: activityLog.duration,
            type: activityLog.type,
            vigorous: vigorous,
            earnedMinutes: activityLog.earnedMinutes,
            enjoyed: activityLog.enjoyed,
            effort: activityLog.effort
        }
    }

    public deserialize(data:any):ActivityLog {
        const activityLog:ActivityLog = new ActivityLog();
        activityLog.id = data.id;
        activityLog.start = moment(data.start).toDate();
        activityLog.type = data.type;
        activityLog.duration = data.duration;
        activityLog.earnedMinutes = data.earnedMinutes;
        activityLog.vigorous = data.vigorous;
        activityLog.enjoyed = data.enjoyed;
        activityLog.effort = data.effort;
        return activityLog;
    }

    public sort(logs: Array<ActivityLog>): void {
        logs.sort((a, b) => {
            if (a.start > b.start) {
                return 1;
            }
            if (b.start > a.start) {
                return -1;
            }
            return 0;
        });
    }

}
