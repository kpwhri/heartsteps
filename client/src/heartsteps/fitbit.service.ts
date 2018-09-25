import { Injectable } from "@angular/core";
import { BrowserService } from "@infrastructure/browser.service";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Storage } from "@ionic/storage";

const storageKey: string = 'fitbit-id'

@Injectable()
export class FitbitService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private browser: BrowserService,
        private storage: Storage
    ) {}

    private getAuthorizationToken(): Promise<string> {
        return this.heartstepsServer.post(this.heartstepsServer.makeUrl('fitbit/authorize/generate'), {})
        .then((response) => {
            console.log(response.token);
            return response.token;
        })
    }

    authorize():Promise<boolean> {
        return this.getAuthorizationToken()
        .then((token: string)=> {
            const url = this.heartstepsServer.makeUrl('fitbit/authorize/' + token);
            return this.browser.open(url);
        })
        .then(() => {
            return this.updateAuthorization()
        })
        .then((fitbitId: string) => {
            return Promise.resolve(true);
        })
        .catch(() => {
            return Promise.reject(false);
        });
    }

    updateAuthorization(): Promise<string> {
        return Promise.resolve('1234')
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
