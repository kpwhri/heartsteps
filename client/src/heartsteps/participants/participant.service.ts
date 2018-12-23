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

    public participant:Subject<any>;

    constructor(
        private storage:StorageService,
        private profileService: ProfileService
    ) {
        this.participant = new Subject();
    }

    update():Promise<boolean> {
        return this.isEnrolled()
        .then(() => {
            return this.profileService.isComplete()
            .then(() => {
                this.participant.next({
                    enrolled: true,
                    profileComplete: true
                })
                return true;
            })
            .catch(() => {
                this.participant.next({
                    enrolled: true,
                    profileComplete: false
                })
                return true;
            })
        })
        .catch(() => {
            this.participant.next(false)
            return true;
        })
    }

    remove():Promise<boolean> {
        return this.profileService.remove()
        .then(() => {
            return this.storage.remove(storageKey);
        })
        .then(() => {
            this.participant.next(false);
            return true;
        });
    }

    setHeartstepsId(heartstepsId:string):Promise<boolean> {
        return this.storage.set(storageKey, heartstepsId)
        .then(() => {
            return this.profileService.load();
        })
        .then(() => {
            return this.update();
        });
    }

    getHeartstepsId():Promise<string> {
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

    isEnrolled():Promise<boolean> {
        return this.getHeartstepsId()
        .then(() => {
            return Promise.resolve(true)
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }
}