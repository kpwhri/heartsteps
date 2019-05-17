import { Injectable } from "@angular/core";
import { Subject } from "rxjs/Subject";
import { ProfileService } from "./profile.factory";
import { StorageService } from "@infrastructure/storage.service";

export class Participant{
    profileComplete: boolean;
}

const storageKey = 'heartsteps-id'

@Injectable()
export class ParticipantService {

    public participant:Subject<Participant>;

    constructor(
        private storage:StorageService,
        private profileService: ProfileService
    ) {
        this.participant = new Subject();
    }

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
        return this.profileService.isComplete()
        .then(() => {
            return {
                profileComplete: true
            };
        })
        .catch(() => {
            return {
                profileComplete: false
            };
        });
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
            return this.profileService.load();
        })
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
