import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";

const storageKey = 'fitbit-watch'

@Injectable()
export class FitbitWatchService {

    constructor(
        private storageService: StorageService
    ) {}

    public isInstalled(): Promise<boolean> {
        return this.storageService.get(storageKey)
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.reject('Fitbit watch not setup');
        });
    }

    public markInstalled(): Promise<boolean> {
        return this.storageService.set(storageKey, true)
        .then(() => {
            return true
        });
    }

}
