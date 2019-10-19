import { Injectable } from "@angular/core";
import { BrowserService } from "@infrastructure/browser.service";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Storage } from "@ionic/storage";
import { Platform } from "ionic-angular";

const storageKey: string = 'fitbit-account'

@Injectable()
export class FitbitService {

    private redirectURL: string = '/';

    constructor(
        private heartstepsServer: HeartstepsServer,
        private browser: BrowserService,
        private storage: Storage,
        private platform: Platform
    ) {}

    public setRedirectURL(url: string) {
        this.redirectURL = url;
    }

    public authorize():Promise<boolean> {
        if (this.platform.is('cordova')) {
            return this.openBrowser()
            .then(() => {
                return this.isAuthorized();
            });
        } else {
            return this.redirectBrowser();
        }
    }

    private getURL(): Promise<string> {
        return this.getAuthorizationToken()
        .then((token) => {
            return this.heartstepsServer.makeUrl('fitbit/authorize/' + token);
        })
    }

    private openBrowser(): Promise<void> {
        return this.getURL()
        .then((url) => {
            const browserPromise = this.browser.openAndWait(url)
            .then(() => {
                this.updateAuthorization()
            });
            return Promise.race([
                browserPromise,
                this.waitForAuthorization()
            ])
            .then(() => {
                return undefined;
            })    
        });
    }

    private redirectBrowser(): Promise<boolean> {
        return this.getURL()
        .then((url) => {
            this.browser.open(url + '?redirect=' + this.redirectURL);
            return new Promise<boolean>((resolve) => {
                setTimeout(() => {
                    resolve(true);
                }, 2000);
            });  
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
            const interval = setInterval(() => {
                this.updateAuthorization()
                .then(() => {
                    resolve(true);
                });
            }, 2000);
        });
    }

    public updateAuthorization(): Promise<string> {
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
