import { Injectable } from '@angular/core';
import { Storage } from '@ionic/storage';

@Injectable()
export class AuthorizationService {

    constructor(private storage:Storage) {
        
    }

    isAuthorized(): Promise<any> {
        return new Promise((resolve, reject) => {
            this.getAuthorization()
            .then(resolve)
            .catch(reject);
        })
    }

    setAuthorization(token:string) {
        this.storage.set('auth-token', token);
    }

    getAuthorization():Promise<string> {
        return new Promise((resolve, reject) => {
            this.storage.get('auth-token')
            .then((token) => {
                if(token) {
                    resolve(token);
                } else {
                    reject();
                }
            })
            .catch(reject);
        })
    }

    removeAuthorization() {
        this.storage.remove('auth-token');
    }
}