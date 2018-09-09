import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Storage } from "@ionic/storage";
import { Injectable } from "@angular/core";

const storageKey: string = 'activity-types';

@Injectable()
export class ActivityTypeService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private storage: Storage
    ) {}

    load() {
        this.heartstepsServer.get('activity/types')
        .then((response: Array<any>) => {
            return this.storage.set(storageKey, response);
        });
    }

    get() {
        return this.storage.get(storageKey)
        .then((types) => {
            if (types) {
                return types;
            }
        })
    }
}