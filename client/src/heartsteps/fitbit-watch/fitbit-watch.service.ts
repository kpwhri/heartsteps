import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";

const storageKey = 'watch-app-installed'

@Injectable()
export class FitbitWatchService {

    constructor(
        private storageService: StorageService
    ) {}

    public isInstalled(): Promise<boolean> {
        return this.wasMarkedInstalled()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.reject('Fitbit watch not setup');
        });
    }

    // This is being used to keep track if participants 
    // installed the app before completing baseline
    public wasMarkedInstalled(): Promise<void> {
        return this.storageService.get('fitbit-watch')
        .then(() => {
            return undefined;
        });
    }

}
