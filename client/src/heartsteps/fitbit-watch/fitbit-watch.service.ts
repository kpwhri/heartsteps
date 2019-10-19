import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { BrowserService } from "@infrastructure/browser.service";

const storageKey = 'watch-app-installed'

@Injectable()
export class FitbitWatchService {

    constructor(
        private storageService: StorageService,
        private browserService: BrowserService
    ) {}

    public openWatchInstallPage() {
        const url = 'https://gam.fitbit.com/gallery/clock/0bd06f9e-2adc-4391-ab05-d177dda1a167';
        this.browserService.open_external(url);
    }

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
