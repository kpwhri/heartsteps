import { Injectable } from "@angular/core";
import { BrowserService } from "@infrastructure/browser.service";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Storage } from "@ionic/storage";
import { NotificationService } from "@heartsteps/notification.service";
import { Subscription } from "rxjs";

const storageKey: string = 'fitbit-account'

@Injectable()
export class FitbitService {

    constructor(
        private notificationService: NotificationService,
        private heartstepsServer: HeartstepsServer,
        private browser: BrowserService,
        private storage: Storage
    ) {}

    private getAuthorizationToken(): Promise<string> {
        return this.heartstepsServer.post('fitbit/authorize/generate', {})
        .then((response) => {
            console.log(response.token);
            return response.token;
        })
    }

    authorize():Promise<boolean> {
        return new Promise((resolve, reject) => {
            let notificationSubscription:Subscription = this.notificationService.dataMessage.subscribe((data) => {
                if(data.fitbit_id) {
                    this.storage.set(storageKey, data.fitbit_id)
                    .then(() => {
                        notificationSubscription.unsubscribe();
                        this.notificationService = null;
                        resolve(true);
                        this.browser.close();
                    });
                }
            });
            
            return this.getAuthorizationToken()
            .then((token: string)=> {
                const url = this.heartstepsServer.makeUrl('fitbit/authorize/' + token);
                return this.browser.open(url);
            })
            .then(() => {
                return this.updateAuthorization()
            })
            .then((fitbitId: string) => {
                resolve(true);
            })
            .catch(() => {
                reject("Fitbit authorization failed");
            })
            .then(() => {
                if(notificationSubscription) {
                    notificationSubscription.unsubscribe();
                }
            });
        });
    }

    updateAuthorization(): Promise<string> {
        return this.heartstepsServer.get('fitbit/account')
        .then((response) => {
            return this.storage.set(storageKey, response.fitbit);
        }).catch((error) => {
            console.log(error);
            console.log("update fitbit authorization failed");
        });
    }

    isAuthorized(): Promise<boolean> {
        return this.storage.get(storageKey)
        .then((fitbitId) => {
            if(fitbitId) {
                return Promise.resolve(true);
            } else {
                return Promise.reject(false);
            }
        })
        .catch(() => {
            return Promise.reject(false);
        });
    }

}
