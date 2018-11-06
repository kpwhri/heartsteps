import { Injectable } from '@angular/core';
import { HeartstepsServer } from '../infrastructure/heartsteps-server.service';
import { ParticipantService } from './participant.service';

@Injectable()
export class EnrollmentService {

    constructor(
        private heartstepsServer:HeartstepsServer,
        private participantService:ParticipantService
    ) {}

    enroll(token:String, birthYear:Number):Promise<boolean> {
        const postData = {
            enrollmentToken: token
        };

        if(birthYear) {
            postData['birthYear'] = birthYear
        }
        
        return this.heartstepsServer.post('enroll' , postData)
        .then((data) => {
            return this.participantService.setHeartstepsId(data.heartstepsId);
        })
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.reject(false);
        });
    }
}