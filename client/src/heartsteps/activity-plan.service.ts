import { Injectable } from "@angular/core";
import * as moment from 'moment';
import { Storage } from "@ionic/storage";
import { DateFactory } from "@heartsteps/date.factory";

const storageKey = 'activityPlans';

@Injectable()
export class ActivityPlanService {

    constructor(
        private storage:Storage,
        private dateFactory:DateFactory
    ){}

    getPlansForDate(date:Date):Promise<any> {
        return this.storage.get(storageKey)
        .then((plans) => {
            let plansForDate = []
            plans.forEach((plan) => {
                if(plan.date == date) {
                    plansForDate.push(plan)
                }
            })
            return plansForDate
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
            return plan
        })
    }

    updatePlan(plan) {

    }

    deletePlan(plan) {

    }

}