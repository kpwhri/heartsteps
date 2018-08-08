import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import { Subject } from "rxjs/Subject";
import { Observable } from "rxjs/Observable";

const storageKey = 'heartsteps-participant'

@Injectable()
export class ParticipantService {

    private enrolled:boolean;
    private onboarded:boolean;

    private subject:Subject<any>;

    constructor(private storage:Storage) {
        this.enrolled = false;
        this.onboarded = false;

        this.subject = new Subject();
    }

    getProfile():Promise<any> {
        let profile = {}
        
        return Promise.resolve(profile) 
    }

    onChange():Observable<any> {
        return this.subject.asObservable();
    }

    refresh():Promise<boolean> {
        return this.storage.get(storageKey)
        .then((data) => {
            return this.update(data)
        })
        .catch(() => {
            this.subject.next();
            return Promise.resolve(true);
        })
    }

    update(data:any):Promise<boolean> {
        if(data.heartstepsId) {
            this.enrolled = true;
        }

        if(data.onboarded) {
            this.onboarded = true;
        }

        this.subject.next();
        return Promise.resolve(true);
    }

    set(data:any):Promise<boolean> {
        return this.storage.set(storageKey, data)
        .then((data) => {
            return this.update(data);
        });
    }

    finishOnboard():Promise<boolean> {
        return this.storage.get(storageKey)
        .then((data) => {
            data.onboarded = true;
            return this.set(data);
        })
    }

    getParticipantId():Promise<string> {
        return this.storage.get(storageKey)
        .then((participant) => {
            return participant.heartstepsId;
        });
    }

    isEnrolled():boolean {
        return this.enrolled;
    }

    isOnboarded():boolean {
        return this.enrolled && this.onboarded;
    }
}