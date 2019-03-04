import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { ActivityPlan } from "./activity-plan.model";
import * as moment from 'moment';
import { Observable, BehaviorSubject } from "rxjs";
import { DocumentStorageService, DocumentStorage } from "@infrastructure/document-storage.service";
import { ActivityLogService } from "@heartsteps/activity-logs/activity-log.service";
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";

@Injectable()
export class ActivityPlanService {
    private plans:BehaviorSubject<Array<ActivityPlan>> = new BehaviorSubject([]);
    private storage:DocumentStorage

    constructor(
        private heartstepsServer:HeartstepsServer,
        private activityLogService: ActivityLogService,
        documentStorage: DocumentStorageService
    ) {
        this.storage = documentStorage.create('heartsteps-activity-plans');
        this.loadPlans();
    }

    public get(id:string) {
        return this.storage.get(id)
        .then((data) => {
            return this.deserializeActivityPlan(data);
        })
        .catch(() => {
            return this.fetch(id);
        });
    }

    public fetch(id:string):Promise<ActivityPlan> {
        return this.heartstepsServer.get('/activity/plans/'+id)
        .then((data) => {
            return this.deserializeActivityPlan(data);
        });
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
        return this.save(activityPlan)
        .then((plan) => {
            if(activityPlan.activityLogId) {
                const mockActivityLog = new ActivityLog();
                mockActivityLog.id = activityPlan.activityLogId;
                mockActivityLog.start = activityPlan.start;
                this.activityLogService.deleted.emit(mockActivityLog);
            }
            return plan;
        });
    }

    complete(activityPlan:ActivityPlan):Promise<ActivityPlan> {
        activityPlan.complete = true;
        return this.save(activityPlan)
        .then((plan) => {
            if(plan.activityLogId) {
                return this.activityLogService.getLog(plan.activityLogId)
                .then((log) => {
                    this.activityLogService.updated.emit(log);
                    return Promise.resolve()
                })
                .catch(() => {})
                .then(() => {
                    return plan;
                });
            }
            return plan;
        });
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
            date: moment(activityPlan.date).format("YYYY-MM-DD"),
            timeOfDay: activityPlan.timeOfDay,
            type: activityPlan.type,
            duration: activityPlan.duration,
            vigorous: activityPlan.vigorous,
            complete: activityPlan.complete,
            activityLogId: activityPlan.activityLogId || undefined
        };
    }

    private deserializeActivityPlan(data:any):ActivityPlan {
        const activityPlan = new ActivityPlan();
        activityPlan.id = data.id;
        activityPlan.date = moment(data.date, 'YYYY-MM-DD').toDate();
        activityPlan.timeOfDay = data.timeOfDay;
        activityPlan.type = data.type;
        activityPlan.duration = data.duration;
        activityPlan.vigorous = data.vigorous || false;
        activityPlan.complete = data.complete || false;
        activityPlan.activityLogId = data.activityLogId || undefined;

        return activityPlan
    }

}
