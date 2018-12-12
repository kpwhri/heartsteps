import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";

const storageKey: string = 'activity-types';

export class ActivityType {
    title: string;
    name: string;
}

@Injectable()
export class ActivityTypeService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private storage: StorageService
    ) {}

    load():Promise<Array<ActivityType>> {
        return this.heartstepsServer.get('activity/types')
        .then((response: Array<any>) => {
            return this.storage.set(storageKey, response);
        })
        .then((types) => {
            return this.castActivityTypes(types);
        });
    }

    get():Promise<Array<ActivityType>> {
        return this.storage.get(storageKey)
        .then((types:Array<any>) => {
            return this.castActivityTypes(types);
        })
        .catch(() => {
            return this.load();
        });
    }

    private castActivityTypes(list:Array<any>):Array<ActivityType> {
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