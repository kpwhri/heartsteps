import { Injectable } from '@angular/core';
import { Storage } from '@ionic/storage';

@Injectable()
export class AuthorizationService {

    private retryMethod: Function;
    private retryPromise: Promise<boolean>;

    constructor(
        private storage: Storage
    ) { }

    isAuthorized(): Promise<any> {
        return new Promise((resolve, reject) => {
            this.getAuthorization()
                .then(resolve)
                .catch(reject);
        })
    }

    retryAuthorization(): Promise<boolean> {
        if (this.retryPromise) {
            return this.retryPromise;
        }
        if (this.retryMethod) {
            this.retryPromise = this.retryMethod();
            return this.retryPromise;
        }
        return Promise.reject("Authorization failed");
    }

    onRetryAuthorization(fn: Function): void {
        this.retryMethod = fn;
    }

    removeRetryAuthorization(): void {
        this.retryMethod = null;
    }

    setAuthorization(token: string) {
        this.storage.set('auth-token', token);
    }

    getAuthorization(): Promise<string> {
        return new Promise((resolve, reject) => {
            this.storage.get('auth-token')
                .then((token) => {
                    if (token) {
                        console.log("[AuthorizationService] getAuthorization(): token: " + token);
                        resolve(token);
                    } else {
                        reject();
                    }
                })
                .catch(reject);
        })
    }

    removeAuthorization(): Promise<void> {
        return this.storage.remove('auth-token');
    }
}