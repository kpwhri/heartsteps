import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { ActivityPlan } from "./activity-plan.model";
import * as moment from 'moment';
import { Observable, Subject, BehaviorSubject } from "rxjs";
import { DocumentStorageService, DocumentStorage } from "@infrastructure/document-storage.service";

@Injectable()
export class ActivityPlanService {
    private plans:BehaviorSubject<Array<ActivityPlan>> = new BehaviorSubject([]);
    private storage:DocumentStorage

    constructor(
        private heartstepsServer:HeartstepsServer,
        documentStorage: DocumentStorageService
    ) {
        this.storage = documentStorage.create('heartsteps-activity-plans');
        this.loadPlans();
    }

    save(activityPlan:ActivityPlan):Promise<ActivityPlan> {
        return this.updateOrCreatePlan(activityPlan)
        .then((activityPlan:ActivityPlan) => {
            return this.storePlan(activityPlan)
            .then(() => {
                return activityPlan;
            });
        });
    }

    delete(activityPlan:ActivityPlan):Promise<boolean> {
        return this.heartstepsServer.delete('activity/plans/' + activityPlan.id)
        .then(() => {
            return this.storage.remove(activityPlan.id)
        })
        .then(() => {
            return this.loadPlans()
        })
        .then(() => {
            return true;
        });
    }

    uncomplete(activityPlan:ActivityPlan):Promise<ActivityPlan> {
        activityPlan.complete = false;
        return this.save(activityPlan);
    }

    complete(activityPlan:ActivityPlan):Promise<ActivityPlan> {
        activityPlan.complete = true;
        return this.save(activityPlan);
    }

    getPlansOn(date:Date):Observable<Array<ActivityPlan>> {
        const plansSubject:BehaviorSubject<Array<ActivityPlan>> = new BehaviorSubject([]);
        this.plans.subscribe((allPlans:Array<ActivityPlan>) => {
            const plans:Array<ActivityPlan> = allPlans.filter((plan) => {
                if(moment(date).format("YYYY-MM-DD") === moment(plan.start).format("YYYY-MM-DD")) {
                    return true;
                } else {
                    return false;
                }
            });
            plansSubject.next(plans);
        });
        return plansSubject;
    }

    getPlans(startDate:Date, endDate:Date):Promise<Array<ActivityPlan>> {
        return this.heartstepsServer.get('activity/plans', {
            start: startDate.toISOString(),
            end: endDate.toISOString()
        })
        .then((response: Array<any>) => {
            const plans:Array<ActivityPlan> = [];
            const plansObject:any = {};
            response.forEach((plan: any) => {
                plansObject[plan.id] = plan;
                plans.push(this.deserializeActivityPlan(plan));
            });
            return this.storage.setMany(plansObject)
            .then(() => {
                return this.loadPlans()
            })
            .then(() => {
                return plans;
            });
        });
    }

    private updateOrCreatePlan(activityPlan:ActivityPlan):Promise<ActivityPlan> {
        if(activityPlan.id) {
            return this.updatePlan(activityPlan);
        } else {
            return this.createPlan(activityPlan);
        }
    }

    private createPlan(activityPlan:ActivityPlan):Promise<ActivityPlan> {
        return this.heartstepsServer.post(
            '/activity/plans',
            this.serializeActivityPlan(activityPlan)
        )
        .then((data:any) => {
            const activityPlan = this.deserializeActivityPlan(data)
            return activityPlan;
        });
    }

    private updatePlan(activityPlan:ActivityPlan):Promise<ActivityPlan> {
        return this.heartstepsServer.post(
            '/activity/plans/' + activityPlan.id,
            this.serializeActivityPlan(activityPlan)   
        )
        .then((data:any) => {
            const activityPlan = this.deserializeActivityPlan(data);
            return activityPlan;
        });
    }

    private loadPlans():Promise<Array<ActivityPlan>> {
        return this.storage.getAll()
        .then((data) => {
            let plans:Array<ActivityPlan> = Object.keys(data).map((key:string) => {
                return this.deserializeActivityPlan(data[key]);
            });
            plans = this.sortPlans(plans);
            this.plans.next(plans);
            return plans;
        });
    }

    private storePlan(plan:ActivityPlan):Promise<ActivityPlan> {
        return this.storage.set(plan.id, this.serializeActivityPlan(plan))
        .then(() => {
            return this.loadPlans();
        })
        .then(() => {
            return plan;
        });
    }

    private sortPlans(plans:Array<ActivityPlan>):Array<ActivityPlan> {
        plans.sort((planA:ActivityPlan, planB:ActivityPlan) => {
            if (planA.start > planB.start) return 1;
            if (planB.start > planA.start) return -1;
            return 0;
        })
        return plans;
    }

    private serializeActivityPlan(activityPlan:ActivityPlan):any {
        return {
            id: activityPlan.id,
            type: activityPlan.type,
            start: activityPlan.start.toISOString(),
            duration: activityPlan.duration,
            vigorous: activityPlan.vigorous,
            complete: activityPlan.complete
        };
    }

    private deserializeActivityPlan(data:any):ActivityPlan {
        const activityPlan = new ActivityPlan();
        activityPlan.id = data.id;
        activityPlan.type = data.type;
        activityPlan.duration = data.duration;
        activityPlan.vigorous = data.vigorous || false;
        activityPlan.complete = data.complete || false;

        if(data.start) {
            const localMoment = moment.utc(data.start).local();
            activityPlan.start = new Date(localMoment.toString());
        } else {
            activityPlan.start = new Date();
        }

        return activityPlan
    }

}
