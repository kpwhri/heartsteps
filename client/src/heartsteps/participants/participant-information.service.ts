import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { StorageService } from "@infrastructure/storage.service";


@Injectable()
export class ParticipantInformationService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private storage: StorageService
    ) {}

    public load(): Promise<boolean> {
        return this.heartstepsServer.get('information')
        .then((data) => {
            return this.setStaff(data['staff']);
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
