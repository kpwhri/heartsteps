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

    authorizationService: AuthorizationService;

    constructor(authorizationService:AuthorizationService) {}

    enroll(enrollment_token:String) {
        console.log(process.env.HEARTSTEPS_URL);
        return axios.post("http://localhost:8080/enroll",{
            enrollment_token: enrollment_token
        })
        .then((response) => {
            console.log(response);
            this.authorizationService.setAuthToken(response.data.enrollment_token);
            return true;
        })
        .catch((error) => {
            console.log(error);
            return false;
        })
    }
}