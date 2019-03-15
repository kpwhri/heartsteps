import { Injectable } from "@angular/core";
import { BrowserService } from "@infrastructure/browser.service";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Storage } from "@ionic/storage";

const storageKey: string = 'fitbit-account'

@Injectable()
export class FitbitService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private browser: BrowserService,
        private storage: Storage
    ) {}

    authorize():Promise<boolean> {
        return this.getAuthorizationToken()
        .then((token: string)=> {
            const url = this.heartstepsServer.makeUrl('fitbit/authorize/' + token);
            return this.browser.open(url);
        })
        .then(() => {
            return this.updateAuthorization()
        })
        .then(() => {
            return Promise.resolve(true);
        })
        .catch(() => {
            return Promise.reject("Fitbit authorization failed");
        });
    }

    private getAuthorizationToken(): Promise<string> {
        return this.heartstepsServer.post('fitbit/authorize/generate', {})
        .then((response) => {
            return response.token;
        })
    }

    updateAuthorization(): Promise<string> {
        return this.heartstepsServer.get('fitbit/account')
        .then((response) => {
            return this.storage.set(storageKey, response.fitbit);
        }).catch((error) => {
            return Promise.reject(error);
        });
    }

    remove():Promise<boolean> {
        // Tell server to stop pulling fitbit data
        return this.storage.remove(storageKey);
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
