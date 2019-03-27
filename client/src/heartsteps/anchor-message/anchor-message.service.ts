import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { DateFactory } from "@infrastructure/date.factory";

@Injectable()
export class AnchorMessageService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private dateFactory: DateFactory
    ) {}

    public get(date?: Date): Promise<string> {
        if (!date) {
            date = new Date();
        }

        return this.heartstepsServer.get('anchor-message/' + this.dateFactory.formatDate(date))
        .then((data) => {
            return data['message']
        })
        .catch(() => {
            return Promise.reject('No anchor message');
        });
    }

}
