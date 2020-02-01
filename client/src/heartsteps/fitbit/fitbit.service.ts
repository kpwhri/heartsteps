import { Injectable } from "@angular/core";
import { BrowserService } from "@infrastructure/browser.service";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Platform } from "ionic-angular";
import { ReplaySubject } from "rxjs";
import { StorageService } from "@infrastructure/storage.service";
import moment from "moment";

const storageKey: string = 'fitbit-account-details'

export class FitbitAccount {
    id: string;
    isAuthorized: boolean;
    firstUpdated: Date;
    lastUpdated: Date;
    lastDeviceUpdate: Date;
}

@Injectable()
export class FitbitService {

    private redirectURL: string = '/';
    public account: ReplaySubject<FitbitAccount> = new ReplaySubject(1);

    constructor(
        private heartstepsServer: HeartstepsServer,
        private browser: BrowserService,
        private storageService: StorageService,
        private platform: Platform
    ) {
        this.getAccount()
        .then((account) => {
            this.account.next(account);
        })
    }

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

    public updateAuthorization(): Promise<FitbitAccount> {
        return this.heartstepsServer.get('fitbit/account')
        .then(() => {
            return this.updateFitbitAccount();
        }).catch((error) => {
            return Promise.reject(error);
        });
    }

    private getAccount(): Promise<FitbitAccount> {
        return this.storageService.get(storageKey)
        .then((data) => {
            return this.deserializeAccount(data);
        });
    }

    private saveAccount(account: FitbitAccount): Promise<void> {
        return this.storageService.set(storageKey, this.serializeAccount(account));
    }

    private serializeAccount(account: FitbitAccount): any {
        return {
            'id': account.id,
            'isAuthorized': account.isAuthorized,
            'firstUpdated': account.firstUpdated,
            'lastUpdated': account.lastUpdated,
            'lastDeviceUpdate': account.lastDeviceUpdate,
        }
    }

    private deserializeAccount(data: any): FitbitAccount {
        const account = new FitbitAccount();
        account.id = data.id;
        account.isAuthorized = data.isAuthorized;
        if(data.firstUpdated) account.firstUpdated = moment(data.firstUpdated).toDate();
        if(data.lastUpdated) account.lastUpdated = moment(data.lastUpdated).toDate();
        if(data.lastDeviceUpdate) account.lastDeviceUpdate = moment(data.lastDeviceUpdate).toDate();
        return account;
    }

    public remove():Promise<boolean> {
        // Tell server to stop pulling fitbit data
        return this.storageService.remove(storageKey);
    }

    public removeFitbitAuthorization(): Promise<void> {
        return this.remove()
        .then(() => {
            this.account.next(undefined);
            return undefined;
        })
    }

    public isAuthorized(): Promise<boolean> {
        return this.storageService.get(storageKey)
        .then((fitbitId) => {
            return Promise.resolve(true);
        });
    }

    public updateFitbitAccount(): Promise<FitbitAccount> {
        return this.heartstepsServer.get('fitbit/account')
        .then((data) => {
            const account = this.deserializeAccount({
                id: data['id'],
                firstUpdated: data['firstUpdated'],
                lastUpdated: data['lastUpdated'],
                lastDeviceUpdate: data['lastDeviceUpdate']
            });
            return this.saveAccount(account)
            .then(() => {
                this.account.next(account);
                return account;
            });
        });
    }

}
