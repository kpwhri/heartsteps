import { Injectable } from '@angular/core';
import { HeartstepsServer } from './heartsteps-server.service';



@Injectable()
export class EnrollmentService {

    constructor(private heartstepsServer:HeartstepsServer) {}

    enroll(enrollment_token:String):Promise<any> {
        return new Promise((resolve, reject) => {            
            return this.heartstepsServer.http.post('enroll' ,{
                enrollment_token: enrollment_token
            })
            .then(resolve)
            .catch(reject);
        })
    }
}