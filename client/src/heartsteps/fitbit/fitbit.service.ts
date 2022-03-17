import { Injectable } from '@angular/core';
import { BrowserService } from '@infrastructure/browser.service';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';
import { ReplaySubject } from 'rxjs';
import { StorageService } from '@infrastructure/storage.service';
import moment from 'moment';

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

    private redirectURL: string;
    public account: ReplaySubject<FitbitAccount> = new ReplaySubject(1);

    constructor(
        private heartstepsServer: HeartstepsServer,
        private browser: BrowserService,
        private storageService: StorageService
    ) {}

    public setup(): Promise<void> {
        return this.getAccount()
        .then((account) => {
            this.account.next(account);
        })
        .catch(() => {
            this.account.next(undefined);
        });
    }

    public setRedirectURL(url: string) {
        this.redirectURL = url;
    }

    public startAuthorization():Promise<void> {
        return this.getAuthorizationToken()
        .then((token) => {
            return Promise.resolve(this.heartstepsServer.makeUrl('fitbit/authorize/' + token));
        }) 
        .then((url) => {
            if(this.redirectURL) {
                url += '?redirect=' + this.redirectURL;
            }
            console.log("FitbitService.startAuthorization():", url);
            // this.browser.open(url);
        })
    }

    private getAuthorizationToken(): Promise<string> {
        return this.heartstepsServer.post('fitbit/authorize/generate', {}, false)
        .then((response) => {
            console.log("FitbitService.getAuthorizationToken:", response);
            return response.token;
        })
    }

    public updateAuthorization(): Promise<FitbitAccount> {
        return this.updateFitbitAccount();
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
        return this.getAccount()
        .then((account) => {
            if(account.isAuthorized) {
                return Promise.resolve(true);
            } else {
                return Promise.reject('Not authorized');
            }
        });
    }

    public updateFitbitAccount(): Promise<FitbitAccount> {
        return this.heartstepsServer.get('fitbit/account', undefined, false)
        .then((data) => {
            const account = this.deserializeAccount({
                id: data['id'],
                isAuthorized: data['isAuthorized'],
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
