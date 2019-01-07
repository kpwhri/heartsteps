import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { ActivityPlan } from "./activity-plan.model";
import * as moment from 'moment';
import { Observable, Subject, BehaviorSubject } from "rxjs";
import { DocumentStorageService, DocumentStorage } from "@infrastructure/document-storage.service";

@Injectable()
export class ActivityPlanService {

    private planUpdates:Subject<ActivityPlan> = new Subject();
    private storage:DocumentStorage

    constructor(
        private heartstepsServer:HeartstepsServer,
        documentStorage: DocumentStorageService
    ) {
        this.storage = documentStorage.create('heartsteps-activity-plans');
    }

    save(activityPlan:ActivityPlan):Promise<ActivityPlan> {
        return this.updateOrCreatePlan(activityPlan)
        .then((activityPlan:ActivityPlan) => {
            return this.storage.set(activityPlan.id, this.serializeActivityPlan(activityPlan))
            .then(() => {
                this.planUpdates.next(activityPlan);
                return activityPlan;
            });
        });
    }

    delete(activityPlan:ActivityPlan):Promise<boolean> {
        return this.heartstepsServer.delete('activity/plans/' + activityPlan.id)
        .then(() => {
            return true;
        });
    }

    complete(activityPlan:ActivityPlan):Promise<ActivityPlan> {
        activityPlan.markComplete();
        return this.save(activityPlan);
    }

    getPlansOn(date:Date):Observable<Array<ActivityPlan>> {
        let plans:Array<ActivityPlan> = [];
        const plansSubject:BehaviorSubject<Array<ActivityPlan>> = new BehaviorSubject(plans);
        
        this.planUpdates.subscribe((updatedPlan) => {
            if(moment(date).format("YYYY-MM-DD") !== moment(updatedPlan.start).format("YYYY-MM-DD")) {
                return;
            }

            let replaceIndex:number;
            plans.forEach((plan, index) => {
                if(plan.id === updatedPlan.id) {
                    replaceIndex = index;
                }
            });
            if(replaceIndex === undefined) {
                plans.push(updatedPlan);
            } else {
                plans[replaceIndex] = updatedPlan;
            }

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
            response.forEach((plan: any) => {
                plans.push(this.deserializeActivityPlan(plan));
            });
            return plans;
        });
    }

    private loadPlans():Promise<Array<ActivityPlan>> {
        return this.storage.getAll();
    }

    private updateOrCreatePlan(activityPlan):Promise<ActivityPlan> {
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
