import axios from 'axios'
import { HTTP } from '@ionic-native/http';
import { Injectable } from '@angular/core';
import { AuthorizationService } from './authorization.service';
import { Platform } from 'ionic-angular';
import urljoin from 'url-join';

declare var process: {
    env: {
        HEARTSTEPS_URL: string
    }
}

@Injectable()
export class HeartstepsServer {

    private heartstepsUrl:string
    private http:any;

    constructor(private authorizationService:AuthorizationService, private platform:Platform) {
        this.heartstepsUrl = process.env.HEARTSTEPS_URL;

        if(this.platform.is('ios') || this.platform.is('android')) {
            this.http = new HTTP();
        } else {
            this.http = axios.create();
        }
    }

    makeUrl(uri:string):string {
        return urljoin(this.heartstepsUrl, uri);
    }

    get(url:string):Promise<any> {
        return this.setAuthorizationHeaderToken()
        .then((headers) => {
            if(this.platform.is('ios') || this.platform.is('android')) {
                return this.http.get(this.makeUrl(url), headers)
            } else {
                return this.http.get(this.makeUrl(url), {headers: headers})
            }
        })
        .then((response) => {
            return this.updateAuthorizationToken(response);
        })
        .then((response) => {
            return response.data
        });
    }

    post(url:string, data:any):Promise<any> {
        return this.setAuthorizationHeaderToken()
        .then((headers) => {
            if(this.platform.is('ios') || this.platform.is('android')) {
                return this.http.post(this.makeUrl(url), data, headers)
            } else {
                return this.http.post(this.makeUrl(url), data, {headers: headers})
            }
        })
        .then(this.parseResponse)
        .then((response) => {
            return this.updateAuthorizationToken(response);
        })
        .then((response) => {
            return response.data;
        });
    }

    parseResponse(response) {
        if(typeof response.data === 'string') {
            response.data = JSON.parse(response.data);
        }
        return response;
    }

    setAuthorizationHeaderToken():Promise<any> {
        return this.authorizationService.getAuthorization()
        .then((token) => {
            return {
                Authorization: `Token ${token}`
            };
        })
        .catch(() => {
            return Promise.resolve({});
        });
    }

    updateAuthorizationToken(response:any):any {
        const token:string = response.headers['authorization-token'];
        if(token) {
            this.authorizationService.setAuthorization(token);
        }
        return response
    }

}