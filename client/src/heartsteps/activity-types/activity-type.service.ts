import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { BehaviorSubject } from "rxjs";

const storageKey: string = 'activity-types';

export class ActivityType {
    title: string;
    name: string;
}

@Injectable()
export class ActivityTypeService {

    public activityTypes:BehaviorSubject<Array<ActivityType>> = new BehaviorSubject([]);

    constructor(
        private heartstepsServer: HeartstepsServer,
        private storage: StorageService
    ) {}

    public setup(): Promise<boolean> {
        return this.update()
        .then(() => {
            return true;
        });
    }

    public update():Promise<Array<ActivityType>> {
        return this.getActivityTypes()
        .then((activityTypes) => {
            this.activityTypes.next(activityTypes);
            return activityTypes;
        });
    }

    public load():Promise<Array<ActivityType>> {
        return this.heartstepsServer.get('activity/types')
        .then((response: Array<ActivityType>) => {
            return this.storage.set(storageKey, response);
        })
        .then(() => {
            return this.loadActivityLogCounts();
        })
        .then(() => {
            return this.loadActivityPlanCounts();
        })
        .then(() => {
            return this.update();
        });
    }

    public getActivityTypesByName(): Promise<Array<ActivityType>> {
        return this.getActivityTypes();
    }

    public getActivityLogTypesByMostUsed(): Promise<Array<ActivityType>> {
        return this.getActivityLogOrder()
        .then((activityLogOrder) => {
            return this.getActivityTypes()
            .then((activityTypes) => {
                const reordered = [...activityTypes].sort((a, b) => {
                    const apos = activityLogOrder.indexOf(a.name);
                    const bpos = activityLogOrder.indexOf(b.name);
                    if(apos < bpos) return 1;
                    if(apos > bpos) return -1;
                    return 0;
                });
                return reordered;
            });
        })
        .catch(() => {
            return this.getActivityTypes();
        });
    }

    public getActivityPlanTypesByMostUsed(): Promise<Array<ActivityType>> {
        return this.getActivityPlanOrder()
        .then((activityPlanOrder) => {
            return this.getActivityTypes()
            .then((activityTypes) => {
                const reordered = [...activityTypes].sort((a, b) => {
                    const apos = activityPlanOrder.indexOf(a.name);
                    const bpos = activityPlanOrder.indexOf(b.name);
                    if(apos < bpos) return 1;
                    if(apos > bpos) return -1;
                    return 0;
                });
                return reordered;
            });   
        })
        .catch(() => {
            return this.getActivityTypes();
        });
    }

    private getActivityLogOrder(): Promise<Array<string>> {
        return this.storage.get('activity-log-type-counts')
        .then((counts) => {
            if(counts) {
                const keys = Object.keys(counts).sort((a, b) => {
                    if(counts[a] > counts[b]) return 1;
                    if(counts[a] < counts[b]) return -1;
                    if(a > b) return -1;
                    if(a < b) return 1;
                    return 0;
                });
                return keys;
            } else {
                return [];
            }
        });
    }

    private loadActivityLogCounts(): Promise<void> {
        return this.heartstepsServer.get('activity/logs/summary')
        .then((data) => {
            if (data['activityTypes']) {
                return this.storage.set('activity-log-type-counts', data['activityTypes']);
            } else {
                return this.storage.set('activity-log-type-counts', {});
            }
            
        })
        .then(() => {
            return undefined;
        });
    }

    private getActivityPlanOrder(): Promise<Array<String>> {
        return this.storage.get('activity-plan-type-counts')
        .then((counts) => {
            if(counts) {
                const keys = Object.keys(counts).sort((a, b) => {
                    if(counts[a] > counts[b]) return 1;
                    if(counts[a] < counts[b]) return -1;
                    if(a > b) return -1;
                    if(a < b) return 1;
                    return 0;
                });
                return keys;
            } else {
                return [];
            }
        })
        .catch(() => {
            return [];
        });
    }

    private loadActivityPlanCounts(): Promise<void> {
        return this.heartstepsServer.get('activity/plans/summary')
        .then((data) => {
            if (data['activityTypes']) {
                return this.storage.set('activity-plan-type-counts', data['activityTypes']);
            } else {
                return this.storage.set('activity-plan-type-counts', {});
            }
            
        })
        .then(() => {
            return undefined;
        });
    }


    public get(type:string):Promise<ActivityType> {
        const activityTypes = this.activityTypes.value;
        const activityType = activityTypes.find((activityType) => {
            return activityType.name === type;
        });
        if(activityType) {
            return Promise.resolve(activityType);
        } else {
            return Promise.reject('No matching type');
        }
    }

    public create(type:string): Promise<ActivityType> {
        return this.heartstepsServer.post('activity/types', {
            name: type
        })
        .then((data) => {
            const activityType = this.deserialize(data);
            return this.load()
            .then(() => {
                return activityType;
            })
        });
    }

    private getActivityTypes():Promise<Array<ActivityType>> {
        return this.storage.get(storageKey)
        .then((types:Array<any>) => {
            const activityTypes = this.deserializeActivityTypes(types);
            return this.sortByName(activityTypes);
        })
        .catch(() => {
            return this.load();
        });
    }

    private deserializeActivityTypes(list:Array<any>):Array<ActivityType> {
        const activityTypes:Array<ActivityType> = [];
        list.forEach((item:any) => {
            const activityType = this.deserialize(item);
            activityTypes.push(activityType);
        });
        return activityTypes;
    }

    private deserialize(data:any): ActivityType {
        const activityType = new ActivityType();
        activityType.name = data.name;
        activityType.title = data.title;
        return activityType;
    }

    private sortByName(activityTypes: Array<ActivityType>): Array<ActivityType> {
        return [...activityTypes].sort((a, b) => {
            if(a.name > b.name) return 1;
            if(a.name < b.name) return -1;
            return 0;
        });
    }
}