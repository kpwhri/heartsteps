import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import {BehaviorSubject} from 'rxjs';
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Activity } from "@heartsteps/activity/activity.model";
import { DailySummary } from '@heartsteps/activity/daily-summary.model';

const storageKey = 'activityLogs';

@Injectable()
export class ActivityLogService {

    public logs: BehaviorSubject<Array<Activity>>

    constructor(
        private storage:Storage,
        private heartstepsServer:HeartstepsServer
    ){
        this.logs = new BehaviorSubject([]);
        this.updateSubject();
    }

    getSummary(date: Date): Promise<any> {
        const formattedDate :string = moment(date).format('YYYY-MM-DD');
        return this.heartstepsServer.get('fitbit/' + formattedDate)
        .then((data) => {
            return new DailySummary(data.active_minutes, 0, data.total_steps, 0);
        });
    }

    updateSubject() {
        this.loadActivities()
        .then((activities) => {
            this.logs.next(activities);
        })
    }

    create(activity:Activity):Promise<Activity> {
        return this.heartstepsServer.post('/activity/logs', activity.serialize())
        .then((response:any) => {
            const activity = new Activity(response);
            return this.storeActivity(activity);
        })
        .then((activity:Activity) => {
            this.updateSubject();
            return new Activity(activity);
        })
    }

    update(){}

    delete(){}

    private loadActivities():Promise<Array<Activity>> {
        return this.storage.get(storageKey)
        .then((logs) => {
            if(logs) {
                let activities = [];
                Object.keys(logs).forEach((logId:string) => {
                    let activity = new Activity(logs[logId]);
                    activity.id = logId;
                    activities.push(activity);
                });
                return activities;
            } else {
                return [];
            }
        })
    }

    private storeActivity(activity:Activity):Promise<Activity> {
        return this.storage.get(storageKey)
        .then((logs) => {
            if (!logs) {
                logs = {};
            }
            logs[activity.id] = activity.serialize();
            return this.storage.set(storageKey, logs)
        })
        .then(() => {
            return activity;
        })
    }
}