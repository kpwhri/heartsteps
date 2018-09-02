import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import {BehaviorSubject} from 'rxjs';

const storageKey = 'activityPlans';

@Injectable()
export class ActivityPlanService {

    public plans: BehaviorSubject<Array<any>>

    constructor(
        private storage:Storage
    ){
        this.plans = new BehaviorSubject([]);
        this.updateSubject();
    }

    updateSubject() {
        this.storage.get(storageKey)
        .then((plans) => {
            this.plans.next(plans)
        })
    }

    createPlan(plan):Promise<any> {
        return this.storage.get(storageKey)
        .then((plans) => {
            if(!plans) {
                plans = []
            }
            plans.push(plan)
            return this.storage.set(storageKey, plans)
        })
        .then(() => {
            this.updateSubject()
            return plan
        })
    }

    updatePlan(plan) {

    }

    deletePlan(plan) {

    }

}