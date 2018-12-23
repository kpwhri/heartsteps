import { Injectable } from '@angular/core';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';
import { ParticipantService } from '@heartsteps/participants/participant.service';
import { AuthorizationService } from '@infrastructure/authorization.service';
import { StorageService } from '@infrastructure/storage.service';

@Injectable()
export class EnrollmentService {

    constructor(
        private heartstepsServer:HeartstepsServer,
        private participantService:ParticipantService,
        private authorizationService:AuthorizationService,
        private storage:StorageService
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

    unenroll():Promise<boolean> {
        // TODO unenroll on heartsteps server
        return this.participantService.remove()
        .then(() => {
            return this.authorizationService.removeAuthorization()
        })
        .then(() => {
            return this.storage.clear();
        })
        .then(() => {
            return true;
        });
    }
}