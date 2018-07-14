import { Injectable } from '@angular/core';
import { HeartstepsServer } from '../infrastructure/heartsteps-server.service';
import { ParticipantService } from './participant.service';



@Injectable()
export class EnrollmentService {

    constructor(private heartstepsServer:HeartstepsServer, private participantService:ParticipantService) {}

    enroll(enrollmentToken:String):Promise<boolean> {
        return this.heartstepsServer.post('enroll' ,{
            enrollmentToken: enrollmentToken
        })
        .then((data) => {
            return this.participantService.set({
                heartstepsId: data.heartstepsId
            });
        })
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.reject(false);
        });
    }
}