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

    public activityTypes:BehaviorSubject<Array<ActivityType>>;

    constructor(
        private heartstepsServer: HeartstepsServer,
        private storage: StorageService
    ) {
        this.activityTypes = new BehaviorSubject(null);
        this.get()
        .then((activityTypes) => {
            this.activityTypes.next(activityTypes);
        });
    }

    load():Promise<Array<ActivityType>> {
        return this.heartstepsServer.get('activity/types')
        .then((response: Array<any>) => {
            return this.storage.set(storageKey, response);
        })
        .then((types) => {
            return this.deserializeActivityTypes(types);
        });
    }

    get():Promise<Array<ActivityType>> {
        return this.storage.get(storageKey)
        .then((types:Array<any>) => {
            return this.deserializeActivityTypes(types);
        })
        .catch(() => {
            return this.load();
        });
    }

    getType(type:string):Promise<ActivityType> {
        return this.get()
        .then((types) => {
            const filteredTypes:Array<ActivityType> = types.filter((activityType) => { 
                return activityType.name === type 
            });
            if(filteredTypes.length === 1) {
                return Promise.resolve(filteredTypes[0]);
            } else {
                return Promise.reject("No matching type");
            }
        });
    }

    private deserializeActivityTypes(list:Array<any>):Array<ActivityType> {
        const activityTypes:Array<ActivityType> = [];
        list.forEach((item:any) => {
            const activityType:ActivityType = new ActivityType();
            activityType.name = item.name;
            activityType.title = item.title;
            activityTypes.push(activityType);
        });
        return activityTypes;
    }
}