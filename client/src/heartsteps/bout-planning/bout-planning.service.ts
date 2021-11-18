import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";

const storageKey:string = 'bout-planning';

@Injectable()
export class BoutPlanningService {

    constructor(
        private storage:StorageService,
    ) {}

    public clear():Promise<boolean> {
        return this.storage.remove(storageKey)
        .then(() => {
            return true;
        });
    }
}