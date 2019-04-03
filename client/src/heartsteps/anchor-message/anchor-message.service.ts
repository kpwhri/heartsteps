import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { DateFactory } from "@infrastructure/date.factory";
import { StorageService } from "@infrastructure/storage.service";

const storageKey = 'anchor-message';

@Injectable()
export class AnchorMessageService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private dateFactory: DateFactory,
        private storageService: StorageService
    ) {}

    public get(): Promise<string> {

        return this.retrieve()
        .catch(() => {
            const today = new Date();
            return this.heartstepsServer.get('anchor-message/' + this.dateFactory.formatDate(today))
            .then((data) => {
                const message = data['message']
                return this.set(message, today)
                .then(() => {
                    return message;
                });
            })
            .catch(() => {
                return Promise.reject('AnchorMessageService: Could not get anchor message');
            }); 
        });
    }

    private set(message: string, date: Date): Promise<boolean> {
        return this.storageService.set(storageKey, {
            message: message,
            day: this.dateFactory.formatDate(date)
        });
    }

    private retrieve(): Promise<string> {
        return this.storageService.get(storageKey)
        .then((storedValue) => {
            const message:string = storedValue['message'];
            const day:Date = this.dateFactory.parseDate(storedValue['day']);

            const today = new Date();
            if(this.dateFactory.isSameDay(today, day)) {
                return Promise.resolve(message);
            } else {
                return this.storageService.remove(storageKey)
                .then(() => {
                    return Promise.reject('AnchorMessageService: Not from today');
                });
            }
        })
    }

}
