import axios from 'axios'
import { HTTP } from '@ionic-native/http';
import { Injectable } from '@angular/core';
import { AuthorizationService } from './authorization.service';
import { Platform } from 'ionic-angular';
import urljoin from 'url-join';
import { Subject } from 'rxjs';

declare var process: {
    env: {
        HEARTSTEPS_URL: string
    }
}

@Injectable()
export class HeartstepsServer {

    private heartstepsUrl:string
    private http:any;

    public unauthorized:Subject<boolean>

    constructor(private authorizationService:AuthorizationService, private platform:Platform) {
        this.heartstepsUrl = process.env.HEARTSTEPS_URL;

        this.unauthorized = new Subject();

        if(this.platform.is('ios') || this.platform.is('android')) {
            this.http = new HTTP()
        } else {
            this.http = axios.create()
        }
    }

    makeUrl(uri:string):string {
        return urljoin(this.heartstepsUrl, uri);
    }

    get(url:string, params?:any):Promise<any> {
        if(params) {
            let urlArgs: string = "";
            Object.keys(params).forEach((key) => {
                if (urlArgs != "") {
                    urlArgs += "&";
                }
                urlArgs += key + "=" + params[key]
            })
            url += "?" + urlArgs;
        }
        return this.setAuthorizationHeaderToken()
        .then((headers) => {
            if(this.platform.is('ios') || this.platform.is('android')) {
                return this.http.get(this.makeUrl(url), {}, headers)
            } else {
                return this.http.get(this.makeUrl(url), {headers: headers})
            }
        })
        .then(this.parseResponse)
        .then((response) => {
            return this.updateAuthorizationToken(response);
        })
        .then((response) => {
            return response.data
        })
        .catch((error) => {
            return this.handleError(error);
        });
    }

    post(url:string, data:any):Promise<any> {
        return this.setAuthorizationHeaderToken()
        .then((headers) => {
            if(this.platform.is('ios') || this.platform.is('android')) {
                this.http.setDataSerializer('json')
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
        })
        .catch((error) => {
            return this.handleError(error);
        });
    }

    delete(url:string):Promise<any> {
        return this.setAuthorizationHeaderToken()
        .then((headers) => {
            if(this.platform.is('ios') || this.platform.is('android')) {
                return this.http.delete(this.makeUrl(url), {}, headers);
            } else {
                return this.http.delete(this.makeUrl(url), {headers: headers});
            }
        })
        .catch((error) => {
            return this.handleError(error);
        })
    }

    parseResponse(response) {
        if(typeof response.data === 'string') {
            response.data = JSON.parse(response.data);
        }
        return response;
    }

    handleError(error:any) {
        if(error.response.status === 401) {
            return this.authorizationService.retryAuthorization()
            .catch(() => {
                return Promise.reject(error.message);
            })
        }
        return Promise.reject(error.message);
    }

    setAuthorizationHeaderToken():Promise<any> {
        let headers = {
            'Content-Type': 'application/json'
        }

        return this.authorizationService.getAuthorization()
        .then((token) => {
            headers['Authorization'] = `Token ${token}`
            return headers
        })
        .catch(() => {
            return Promise.resolve(headers);
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