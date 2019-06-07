import { Injectable } from "@angular/core";
import { ProfileService } from "./profile.factory";
import { StorageService } from "@infrastructure/storage.service";
import { ParticipantInformationService } from "./participant-information.service";
import { ContactInformationService } from "@heartsteps/contact-information/contact-information.service";
import { BehaviorSubject } from "rxjs";

export class Participant{
    name: string;
    profileComplete: boolean;
    staff: boolean;
    dateEnrolled: Date;
}

const storageKey = 'heartsteps-id'

@Injectable()
export class ParticipantService {

    public participant:BehaviorSubject<Participant> = new BehaviorSubject(undefined);

    constructor(
        private storage:StorageService,
        private profileService: ProfileService,
        private participantInformationService: ParticipantInformationService,
        private contactInformationService: ContactInformationService
    ) {}

    public getProfile():Promise<any> {
        return this.profileService.get();
    }

    public update():Promise<boolean> {
        return this.isEnrolled()
        .then(() => {
            return this.profileService.load()
        })
        .then(() => {
            return this.getParticipant()
            .then((participant) => {
                this.participant.next(participant);
                return true;
            });
        })
        .catch(() => {
            this.participant.next(null)
            return true;
        })
    }

    private getParticipant():Promise<Participant> {
        return Promise.all([
            this.getProfileComplete(),
            this.getStaffStatus(),
            this.getName(),
            this.participantInformationService.getDateEnrolled()
        ])
        .then((results) => {
            return {
                name: results[2],
                profileComplete: results[0],
                staff: results[1],
                dateEnrolled: results[3]
            }
        });
    }

    private getProfileComplete(): Promise<boolean> {
        return this.profileService.isComplete()
        .catch(() => {
            return Promise.resolve(false);
        });
    }

    private getStaffStatus(): Promise<boolean> {
        return this.participantInformationService.isStaff()
        .catch(() => {
            return Promise.resolve(false);
        })
    }

    private getName(): Promise<string> {
        return this.contactInformationService.get()
        .then((contactInformation:any) => {
            if(contactInformation.name) {
                return Promise.resolve(contactInformation.name);
            } else {
                return Promise.reject('No name set');
            }
        })
        .catch(() => {
            return Promise.resolve(undefined);
        })
    }

    public remove():Promise<boolean> {
        return this.profileService.remove()
        .then(() => {
            return this.storage.remove(storageKey);
        })
        .then(() => {
            this.participant.next(null);
            return true;
        });
    }

    public setHeartstepsId(heartstepsId:string):Promise<boolean> {
        return this.storage.set(storageKey, heartstepsId)
        .then(() => {
            return this.update();
        });
    }

    public getHeartstepsId():Promise<string> {
        return this.storage.get(storageKey)
        .then((heartstepsId) => {
            if(heartstepsId) {
                return heartstepsId;
            } else {
                return Promise.reject(false)
            }
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    public isEnrolled():Promise<boolean> {
        return this.getHeartstepsId()
        .then(() => {
            return Promise.resolve(true)
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    public logout():Promise<boolean> {
        return this.remove()
        .then(() => {
            return this.storage.clear()
        })
        .then(() => {
            return true;
        });
    }
}
