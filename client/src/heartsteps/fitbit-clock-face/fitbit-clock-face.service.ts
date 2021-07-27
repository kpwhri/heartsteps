import * as moment from 'moment';
import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { BrowserService } from '@infrastructure/browser.service';


@Injectable()
export class FitbitClockFaceService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private browserService: BrowserService
    ) {}

    public getClockFace(): Promise<any> {
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
            return Promise.resolve();
        })
        .catch(() => {
            return Promise.reject('Pairing failed');
        });
    }

    public unpair(): Promise<void> {
        return this.heartstepsServer.delete('fitbit-clock-face/pair');
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
