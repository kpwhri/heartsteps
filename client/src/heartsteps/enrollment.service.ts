import axios from 'axios'
import { AuthorizationService } from './authorization.service';
import { Injectable } from '@angular/core';

declare var process: {
    env: {
        HEARTSTEPS_URL: string
    }
}

@Injectable()
export class EnrollmentService {

    constructor(private authorizationService:AuthorizationService) {}

    enroll(enrollment_token:String) :Promise<boolean> {
        return new Promise((resolve, reject) => {
            const url:string = process.env.HEARTSTEPS_URL;
            return axios.post(url+"/enroll",{
                enrollment_token: enrollment_token
            })
            .then((response) => {
                this.authorizationService.setAuthorization(response.data.token);
                resolve();
            })
            .catch((error) => {
                reject();
            });
        })
    }
}