import { Injectable } from "@angular/core";
import {BehaviorSubject} from 'rxjs';
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Activity } from "@heartsteps/activity/activity.model";
import { StorageService } from "@infrastructure/storage.service";

const storageKey = 'activityPlans';

@Injectable()
export class ActivityPlanService {

    public plans: BehaviorSubject<Array<Activity>>

    constructor(
        private storage:StorageService,
        private heartstepsServer:HeartstepsServer
    ){
        this.plans = new BehaviorSubject([]);
        this.updateSubject();
    }

    updateSubject() {
        this.loadPlans()
        .then((plans) => {
            this.plans.next(plans);
        })
    }

    private createPlan(activity:Activity):Promise<Activity> {
        return this.heartstepsServer.post('/activity/plans', activity.serialize())
        .then((response:any) => {
            const activity = new Activity(response);
            return this.storeActivity(activity);
        });
    }

    private updatePlan(activity:Activity):Promise<Activity> {
        return this.heartstepsServer.post(
            '/activity/plans/' + activity.id,
            activity.serialize()   
        )
        .then((response:any) => {
            const activity = new Activity(response);
            return this.storeActivity(activity);
        });
    }

    save(activity:Activity):Promise<Activity> {
        if(activity.id) {
            return this.updatePlan(activity);
        } else {
            return this.createPlan(activity);
        }
    }

    delete(activity:Activity):Promise<boolean> {
        return this.heartstepsServer.delete('activity/plans/' + activity.id)
        .then(() => {
            return this.removeActivity(activity.id);
        });
    }

    complete(activity:Activity):Promise<Activity> {
        return Promise.resolve(activity);
    }

    getPlans(startDate:Date, endDate:Date):Promise<boolean> {
        return this.heartstepsServer.get('activity/plans', {
            start: startDate.toISOString(),
            end: endDate.toISOString()
        })
        .then((response: Array<any>) => {
            let plans = {};
            response.forEach((plan: any) => {
                plans[plan.id] = plan;
            });
            return this.storage.set(storageKey, plans);
        })
        .then(() => {
            this.updateSubject();
            return true;
        })
    }

    private loadPlans():Promise<Array<Activity>> {
        return this.storage.get(storageKey)
        .then((plans) => {
            if (plans) {
                let activities = [];
                Object.keys(plans).forEach((planId:string) => {
                    let activity = new Activity(plans[planId]);
                    activity.id = planId;
                    activities.push(activity);
                });
                return activities;
            } else  {
                return [];
            }
        });
    }

    private storeActivity(activity:Activity):Promise<Activity> {
        return this.storage.get(storageKey)
        .catch(() => {
            return {}
        })
        .then((plans:any) => {
            plans[activity.id] = activity.serialize();
            return this.storage.set(storageKey, plans)
        })
        .then(() => {
            this.updateSubject();
            return activity;
        });
    }

    private removeActivity(activityId:string):Promise<boolean> {
        return this.storage.get(storageKey)
        .then((plans:any) => {
            delete plans[activityId]
            return this.storage.set(storageKey, plans);
        })
        .then(() => {
            this.updateSubject();
            return Promise.resolve(true);
        });
    }

}
