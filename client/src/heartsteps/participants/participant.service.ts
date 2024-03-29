import { Injectable } from "@angular/core";
import { ProfileService } from "./profile.factory";
import { StorageService } from "@infrastructure/storage.service";
import { ParticipantInformationService } from "./participant-information.service";
import { ContactInformationService } from "@heartsteps/contact-information/contact-information.service";
import { ReplaySubject, BehaviorSubject } from "rxjs";
import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";

export class Participant{
    dateEnrolled: Date;
    isLoaded: boolean;
    isSetup: boolean;
    isBaselineComplete: boolean;
    name: string;
    staff: boolean;
}

const storageKey = 'heartsteps-id'

@Injectable()
export class ParticipantService {

    public participant:ReplaySubject<Participant> = new ReplaySubject(1);
    public updatingParticipant:BehaviorSubject<boolean> = new BehaviorSubject(false);

    constructor(
        private storage:StorageService,
        private profileService: ProfileService,
        private participantInformationService: ParticipantInformationService,
        private contactInformationService: ContactInformationService,
        private featureFlagsService: FeatureFlagService
    ) {
        console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'constructor()');
    }

    public get():Promise<Participant> {
        console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'get()');
        return this.getParticipant()
        .then((participant) => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'get()', 'participant=', participant);
            this.participant.next(participant);
            return participant;
        })
        .catch((error) => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'get()', 'error=', error);
            this.participant.next(undefined);
            return Promise.reject(error);
        });
    }

    public getProfile():Promise<any> {
        return this.profileService.get();
    }

    public update():Promise<void> {
        console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'update()');
        this.updatingParticipant.next(true);
        return this.isEnrolled()
        .then(() => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'update()', 'isEnrolled=true');
            return this.loadOrUpdateParticipant()
        })
        .then(() => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'update()', 'loadOrUpdateParticipant()=true');
            return this.getParticipant()
        })
        .then((participant) => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'update()', 'participant=', participant);
            this.participant.next(participant);
        })
        .catch(() => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'update()', 'error');
            this.participant.next(null);
        })
        .then(() => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'update()', 'updatingParticipant=false');
            this.updatingParticipant.next(false);
            return undefined;
        })
    }

    private getParticipant():Promise<Participant> {
        console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'getParticipant()');
        return Promise.all([
            this.getProfileComplete(),
            this.getStaffStatus(),
            this.getName(),
            this.participantInformationService.getDateEnrolled(),
            this.getBaselineComplete(),
            this.getParticipantLoaded()
        ])
        .then((results) => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'getParticipant()', 'results=', results);
            const participant = new Participant();
            participant.isSetup = results[0];
            participant.staff = results[1];
            participant.name = results[2];
            participant.dateEnrolled = results[3];
            participant.isBaselineComplete = results[4];
            participant.isLoaded = results[5];
            return participant
        });
    }

    private getProfileComplete(): Promise<boolean> {
        console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'getProfileComplete()');
        return this.isOnboardComplete()
        .then((isComplete) => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'getProfileComplete()', 'isComplete=', isComplete);
            if(isComplete) {
                return true;
            } else {
                return this.profileService.isComplete()
            }
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }

    private getBaselineComplete(): Promise<boolean> {
        console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'getBaselineComplete()');
        return this.participantInformationService.getBaselineComplete()
        .catch(() => {
            return Promise.resolve(false);
        });
    }

    private getStaffStatus(): Promise<boolean> {
        console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'getStaffStatus()');
        return this.participantInformationService.isStaff()
        .catch(() => {
            return Promise.resolve(false);
        })
    }

    private getName(): Promise<string> {
        console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'getName()');
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
            return true;
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

    public markOnboardComplete(): Promise<void> {
        return this.storage.set('onboard-complete', true);
    }

    public isOnboardComplete(): Promise<boolean> {
        console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'isOnboardComplete()');
        return this.storage.get('onboard-complete')
        .then(() => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'isOnboardComplete()', 'true');
            return true;
        })
        .catch(() => {
            return false;
        });
    }

    private loadOrUpdateParticipant(): Promise<void> {
        console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'loadOrUpdateParticipant()');
        return this.isParticipantLoaded()
        .then(() => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'loadOrUpdateParticipant()', 'isParticipantLoaded=true');
            return this.profileService.update();
        })
        .catch(() => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'loadOrUpdateParticipant()', 'isParticipantLoaded=false');
            return this.profileService.load()
            .then(() => {
                return this.markParticipantLoaded();
            });
        });
    }

    private isParticipantLoaded(): Promise<void> {
        console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'isParticipantLoaded()');
        return this.storage.get('participant-loaded')
        .then(() => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'isParticipantLoaded()', 'true');
            return undefined;
        })
        .catch(() => {
            console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'isParticipantLoaded()', 'false');
            return Promise.reject('Participant not loaded');
        });
    }

    private getParticipantLoaded(): Promise<boolean> {
        console.log('src', 'heartsteps', 'participants', 'participant.service.ts', 'ParticipantService', 'getParticipantLoaded()');
        return this.isParticipantLoaded()
        .then(() => {
            return true;
        })
        .catch(() => {
            return false;
        });
    }

    private markParticipantLoaded(): Promise<void> {
        return this.storage.set('participant-loaded', true);
    }

    public markParticipantNotLoaded(): Promise<void> {
        return this.storage.remove('participant-loaded');
    }
}
