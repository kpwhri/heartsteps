import * as moment from 'moment';
import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { BrowserService } from '@infrastructure/browser.service';
import { StorageService } from '@infrastructure/storage.service';
import { BehaviorSubject, ReplaySubject } from 'rxjs';

class ClockFace {
    pin: string;
}

@Injectable()
export class FitbitClockFaceService {

    public clockFace: BehaviorSubject<ClockFace> = new BehaviorSubject(undefined);

    constructor(
        private heartstepsServer: HeartstepsServer,
        private browserService: BrowserService,
        private storageService: StorageService
    ) {
        this.load();
    }

    private save(clockFace: ClockFace): Promise<ClockFace> {
        return this.storageService.set('fitbit-clock-face', {
            'pin': clockFace.pin
        });
    }

    private load(): Promise<ClockFace> {
        return this.storageService.get('fitbit-clock-face')
        .then((data) => {
            const clockFace = new ClockFace();
            clockFace.pin = data.pin;
            
            this.clockFace.next(clockFace);
            return clockFace;
        })
        .catch(() => {
            this.clockFace.next(undefined);
            return Promise.reject('No clock face');
        });
    }

    private remove(): Promise<void> {
        return this.storageService.remove('fitbit-clock-face');
    }

    public isPaired(): Promise<void> {
        return this.load()
        .then(() => {
            return undefined
        });
    }

    public update(): Promise<void> {
        return this.getClockFace()
        .then((clockFace) => {
            return this.save(clockFace)
        })
        .then(() => {
            return this.load();
        })
        .then(() => {
            return undefined;
        });
    }

    public getClockFace(): Promise<ClockFace> {
        return this.heartstepsServer.get('fitbit-clock-face/pair')
        .then((data) => {
            return {
                'pin': data.pin
            }
        })
        .catch(() => {
            return Promise.reject('No clock face')
        });
    }

    public pairWithPin(pin: string): Promise<void> {
        return this.heartstepsServer.post('fitbit-clock-face/pair', {
            'pin': pin
        })
        .then(() => {
            return this.update();
        })
        .catch(() => {
            return Promise.reject('Pairing failed');
        });
    }

    public unpair(): Promise<void> {
        return this.heartstepsServer.delete('fitbit-clock-face/pair')
        .then(() => {
            this.remove()
        });
    }

    public getLastClockFaceLogs(): Promise<Array<any>> {
        return this.heartstepsServer.get('fitbit-clock-face/step-counts')
        .then((data) => {
            if (data.step_counts && Array.isArray(data.step_counts)) {
                return data.step_counts.map((step_count) => { 
                    return {
                        'time': moment(step_count.time).fromNow(),
                        'steps': step_count.steps
                    }
                });
            } else {
                return Promise.reject('Step counts not returned');
            }
        })
        .catch((error) => {
            return Promise.reject('Http error');
        });
    }

    public openFitbitGallery() {
        this.browserService.open('https://gallery.fitbit.com/details/805f9d8b-98bc-4d93-8107-9b36b31d138d');
    }
}
