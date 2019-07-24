import { Injectable } from "@angular/core";
import { BrowserService } from "@infrastructure/browser.service";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Storage } from "@ionic/storage";
import { Platform } from "ionic-angular";

const storageKey: string = 'fitbit-account'

@Injectable()
export class FitbitService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private browser: BrowserService,
        private storage: Storage,
        private platform: Platform
    ) {}

    authorize():Promise<boolean> {
        return this.getAuthorizationToken()
        .then((token: string)=> {
            let url = this.heartstepsServer.makeUrl('fitbit/authorize/' + token);
            if (!this.platform.is('cordova')) {
                return this.setIsAuthorizing()
                .then(() => {
                    this.browser.open(url + '?redirect=/setup/fitbitAuthorization');
                    return Promise.resolve(true);
                })
            } else {
                this.browser.open(url);
                return this.waitForAuthorization();
            }
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

    private waitForAuthorization(): Promise<boolean> {
        return new Promise((resolve) => {
            const interval = setInterval(function() {
                this.updateAuthorization()
                .then(() => {
                    resolve(true);
                });
            }, 2000);
        });
    }

    private setIsAuthorizing(): Promise<boolean> {
        return this.storage.set('fitbit-is-authorizing', true)
        .then(() => {
            return Promise.resolve(true);
        });
    }

    public isAuthorizing(): Promise<boolean> {
        return this.storage.get('fitbit-is-authorizing')
        .then((value) => {
            if(value) {
                return Promise.resolve(true);
            } else {
                return Promise.reject('Not authorizing');
            }
        });
    }

    public clearIsAuthorizing(): Promise<boolean> {
        return this.storage.remove('fitbit-is-authorizing')
        .then(() => {
            return Promise.resolve(true);
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
