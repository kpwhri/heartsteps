import axios, { AxiosInstance, AxiosResponse, AxiosRequestConfig } from 'axios'
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

        this.http.interceptors.response.use((response) => {
            return this.updateAuthorizationToken(response);
        });

        this.http.interceptors.request.use((config) => {
            return this.setAuthorizationHeaderToken(config);
        });
    }

    setAuthorizationHeaderToken(config:AxiosRequestConfig):Promise<AxiosRequestConfig> {
        return this.authorizationService.getAuthorization()
        .then((token) => {
            config.headers.Authorization = `Token ${token}`;
            return config;
        })
        .catch(() => {
            return Promise.resolve(config);
        });
    }

    updateAuthorizationToken(response:AxiosResponse):AxiosResponse {
        if(response.data.token) {
            let token:string = response.data.token;
            this.authorizationService.setAuthorization(token);
        }
        return response
    }

}