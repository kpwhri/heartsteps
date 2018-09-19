import { Injectable } from "@angular/core";
import { BrowserService } from "@infrastructure/browser.service";
import { HeartstepsNotifications } from "@heartsteps/heartsteps-notifications.service";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Storage } from "@ionic/storage";

const storageKey: string = 'fitbit-id'

@Injectable()
export class FitbitService {

    constructor(
        private notificationService: HeartstepsNotifications,
        private heartstepsServer: HeartstepsServer,
        private browser: BrowserService,
        private storage: Storage
    ) {}

    getAuthorization(heartstepsId: string):Promise<boolean> {
        return new Promise((resolve, reject) => {
            const notificationSubscription = this.notificationService.onMessage().subscribe((payload: any) => {
                if(payload.fitbit_id) {
                    this.storage.set(storageKey, payload.fitbit_id)
                    .then(() => {
                        resolve(true);
                    });
                } else {
                    reject(false);
                }
                notificationSubscription.unsubscribe();
            })

            const fitbitAuthUrl = this.heartstepsServer.makeUrl('fitbit/authorize/user/' + heartstepsId)
            this.browser.open(fitbitAuthUrl);
        });
    }

    isAuthorized(): Promise<boolean> {
        return new Promise((resolve, reject) => {
            this.storage.get(storageKey)
            .then((fitbitId) => {
                if(fitbitId) {
                    resolve(true);
                } else {
                    reject(false);
                }
            })
            .catch(() => {
                reject(false);
            })
        });
    }

}
