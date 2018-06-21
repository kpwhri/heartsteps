import { Injectable } from '@angular/core';
import { Storage } from '@ionic/storage';

@Injectable()
export class AuthorizationService {
    constructor(private storage:Storage) {

    }

    isAuthorized(): Promise<boolean> {
        return new Promise((resolve, reject) => {
            this.storage.get('auth-token')
            .then(() => {
                resolve(true);
            })
            .catch(() => {
                reject(false);
            })
        })
    }

    setAuthToken(token:string) {
        this.storage.set('auth-token', token);
    }
}