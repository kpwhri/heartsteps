import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { BrowserService } from "@infrastructure/browser.service";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { ReplaySubject } from "rxjs";
import moment from "moment";

const storageKey = 'watch-app-installed'

export class FitbitWatch {
    public installed: Date;
    public lastUpdated: Date;
    public lastChecked: Date;

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
        this.getStatus()
        .then((watch)=>{
            this.watch.next(watch);
        })
        .catch(() => {
            
        });
    }

    private loadStatus(): Promise<FitbitWatch> {
        return this.getStatus()
        .then((watch) => {
            this.watch.next(watch);
            return watch;
        })
        .catch(()=>{
            return this.updateStatus();
        });
    }

    private getStatus(): Promise<FitbitWatch> {
        return Promise.reject('not implemented');
    }

    private saveStatus(watch: FitbitWatch): Promise<FitbitWatch> {
        return this.storageService.set('fitbit-watch-status', this.serialize(watch))
        .then(() => {
            return watch;
        });
    }

    public updateStatus(): Promise<FitbitWatch> {
        return this.heartstepsServer.get('watch-app/status')
        .then((data) => {
            const watch = this.deserialize(data);
            watch.lastChecked = new Date();
            return this.saveStatus(watch);
        })
        .then((watch) => {
            this.watch.next(watch);
            return watch;
        });
    }

    private deserialize(data: any): FitbitWatch {
        const watch = new FitbitWatch();
        if (data.installed) {
            watch.installed = moment(data.installed).toDate();
        }
        if (data.lastUpdated) {
            watch.lastUpdated = moment(data.lastUpdated).toDate();
        }
        watch.lastChecked = data.lastChecked;
        return watch;
    }

    private serialize(watch: FitbitWatch): any {
        return {
            installed: watch.installed,
            lastUpdated: watch.lastUpdated,
            lastChecked: watch.lastChecked
        };
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
