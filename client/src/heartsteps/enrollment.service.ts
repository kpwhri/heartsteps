import { Injectable } from '@angular/core';
import { HeartstepsServer } from '../infrastructure/heartsteps-server.service';
import { ParticipantService } from './participant.service';



@Injectable()
export class EnrollmentService {

    constructor(private heartstepsServer:HeartstepsServer, private participantService:ParticipantService) {}

    enroll(enrollment_token:String):Promise<boolean> {
        return this.heartstepsServer.post('enroll' ,{
            enrollment_token: enrollment_token
        })
        .then((data) => {
            return this.participantService.set({
                participant_id: data.participant_id
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