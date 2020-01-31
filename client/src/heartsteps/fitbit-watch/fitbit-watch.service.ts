import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { BrowserService } from "@infrastructure/browser.service";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { ReplaySubject } from "rxjs";

const storageKey = 'watch-app-installed'

export class FitbitWatch {
    public installed: Date;
    public lastUpdated: Date;

    public isInstalled(): boolean {
        if(this.installed) {
            return true;
        } else {
            return false;
        }
    }
}

@Injectable()
export class FitbitWatchService {

    public watch: ReplaySubject<FitbitWatch> = new ReplaySubject(1);

    constructor(
        private heartstepsServer: HeartstepsServer,
        private storageService: StorageService,
        private browserService: BrowserService
    ) {
        this.loadStatus();
    }

    private loadStatus(): Promise<FitbitWatch> {
        return this.udpateStatus()
        .then(this.saveStatus)
        .then((watch) => {
            this.watch.next(watch);
            return watch;
        });
    }

    private saveStatus(watch: FitbitWatch): Promise<FitbitWatch> {
        return Promise.resolve(watch);
    }

    public udpateStatus(): Promise<FitbitWatch> {
        return this.heartstepsServer.get('watch-app/status')
        .then((data) => {
            const watch = new FitbitWatch();
            watch.installed = data.installed;
            watch.lastUpdated = data.lastUpdated;
            return watch;
        });
    }

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
