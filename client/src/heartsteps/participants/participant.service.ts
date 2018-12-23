import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import { Subject } from "rxjs/Subject";
import { Observable } from "rxjs/Observable";
import { ProfileService } from "./profile.factory";


const storageKey = 'heartsteps-id'

@Injectable()
export class ParticipantService {

    private subject:Subject<any>;

    constructor(
        private storage:Storage,
        private profileService: ProfileService
    ) {
        this.subject = new Subject();
    }

    onChange():Observable<any> {
        return this.subject.asObservable();
    }

    update():Promise<boolean> {
        return this.isEnrolled()
        .then(() => {
            return this.profileService.isComplete()
            .then(() => {
                this.subject.next({
                    enrolled: true,
                    profileComplete: true
                })
                return true;
            })
            .catch(() => {
                this.subject.next({
                    enrolled: true,
                    profileComplete: false
                })
                return true;
            })
        })
        .catch(() => {
            this.subject.next(false)
            return true;
        })
    }

    remove():Promise<boolean> {
        return Promise.resolve(true);
    }

    setHeartstepsId(heartstepsId:string):Promise<boolean> {
        return this.storage.set(storageKey, heartstepsId)
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