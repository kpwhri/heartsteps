import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import {BehaviorSubject} from 'rxjs';
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Activity } from "@heartsteps/activity/activity.model";

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

    getSummary(): Promise<any> {
        return Promise.resolve({
            totalSteps: 150,
            totalActiveMinutes: 10
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