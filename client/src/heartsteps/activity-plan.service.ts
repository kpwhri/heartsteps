import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import {BehaviorSubject} from 'rxjs';
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Activity } from "@heartsteps/activity.model";

const storageKey = 'activityPlans';

@Injectable()
export class ActivityPlanService {

    public plans: BehaviorSubject<Array<Activity>>

    constructor(
        private storage:Storage,
        private heartstepsServer:HeartstepsServer
    ){
        this.plans = new BehaviorSubject([]);
        this.updateSubject();
    }

    updateSubject() {
        this.storage.get(storageKey)
        .then((plansRaw) => {
            const plans = this.deserializePlans(plansRaw);
            this.plans.next(plans);
        })
    }

    createPlan(activity:Activity):Promise<Activity> {
        return this.heartstepsServer.post('/activity/plans', activity.serialize())
        .then((response:any) => {
            const activity = new Activity(response);
            return this.storeActivity(activity);
        })
        .then((activity:Activity) => {
            this.updateSubject();
            return new Activity(activity);
        })
    }

    private deserializePlans(plans):Array<Activity> {
        if (plans) {
            let activities = [];
            plans.forEach((plan) => {
                activities.push(new Activity(plan));
            });
            return activities;
        } else  {
            return [];
        }
    }

    private storeActivity(activity:Activity):Promise<Activity> {
        return this.storage.get(storageKey)
        .then((plans) => {
            if (!plans) {
                plans = [];
            }
            plans.push(activity.serialize());
            return this.storage.set(storageKey, plans)
        })
        .then(() => {
            return activity;
        })
    }

    updatePlan(plan) {

    }

    deletePlan(plan) {

    }

}