import axios, { AxiosInstance, AxiosResponse } from 'axios'
import { Injectable } from '@angular/core';
import { AuthorizationService } from './authorization.service';

declare var process: {
    env: {
        HEARTSTEPS_URL: string
    }
}

@Injectable()
export class HeartstepsServer {

    public http:AxiosInstance

    constructor(private authorizationService:AuthorizationService) {
        this.http = axios.create({
            baseURL: process.env.HEARTSTEPS_URL
        });

        this.authorizationService.getAuthorization()
        .then(this.setAuthorizationHeaderToken)
        .catch(() => {});

        this.http.interceptors.response.use((response) => {
            return this.updateAuthorizationToken(response);
        });
    }

    setAuthorizationHeaderToken(token) {
        this.http.defaults.headers['Authorization'] = 'Token ' + token;
    }

    updateAuthorizationToken(response:AxiosResponse):AxiosResponse {
        if(response.data.token) {
            let token:string = response.data.token;
            this.setAuthorizationHeaderToken(token);
            this.authorizationService.setAuthorization(token);
        }
        return response
    }

}