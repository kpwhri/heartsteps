import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { StorageService } from "@infrastructure/storage.service";

import * as moment from 'moment';

@Injectable()
export class ParticipantInformationService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private storage: StorageService
    ) {}

    public load(): Promise<boolean> {
        return this.heartstepsServer.get('information')
        .then((data) => {
            return Promise.all([
                this.setDateEnrolled(data['date_enrolled']),
                this.setStaff(data['staff'])
            ])
        })
        .then(() => {
            return true;
        });
    }

    public isStaff(): Promise<boolean> {
        return this.getStaff()
        .then((isStaff: boolean) => {
            if(isStaff) {
                return Promise.resolve(true);
            } else {
                return Promise.reject('Not staff');
            }
        })
        .catch(() => {
            return Promise.reject('Not staff');
        })
    }

    private setDateEnrolled(enrolled_date_string: string): Promise<boolean> {
        return this.storage.set('date_enrolled', enrolled_date_string)
        .then(() => {
            return true;
        });
    }

    public getDateEnrolled(): Promise<Date> {
        return this.storage.get('date_enrolled')
        .catch(() => {
            return this.load()
            .then(() => {
                return this.storage.get('date_enrolled');
            })
        })
        .then((date_enrolled_string) => {
            return moment(date_enrolled_string, "YYYY-MM-DD").toDate();
        });
    }

    private setStaff(isStaff: boolean): Promise<boolean> {
        return this.storage.set('isStaff', isStaff)
        .then(() => {
            return true;
        });
    }

    private getStaff(): Promise<boolean> {
        return this.storage.get('isStaff')
        .then((isStaff) => {
            return isStaff;
        })
        .catch(() => {
            return Promise.reject('No data');
        });
    }

}
