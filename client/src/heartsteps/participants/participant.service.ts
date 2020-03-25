import { Injectable } from "@angular/core";
import { ProfileService } from "./profile.factory";
import { StorageService } from "@infrastructure/storage.service";
import { ParticipantInformationService } from "./participant-information.service";
import { ContactInformationService } from "@heartsteps/contact-information/contact-information.service";
import { ReplaySubject } from "rxjs";
import { DailySummaryService } from "@heartsteps/daily-summaries/daily-summary.service";
import { FitbitWatchService } from "@heartsteps/fitbit-watch/fitbit-watch.service";

export class Participant{
    dateEnrolled: Date;
    isSetup: boolean;
    isBaselineComplete: boolean;
    name: string;
    staff: boolean;
}

const storageKey = 'heartsteps-id'

@Injectable()
export class ParticipantService {

    public participant:ReplaySubject<Participant> = new ReplaySubject(1);

    constructor(
        private storage:StorageService,
        private profileService: ProfileService,
        private participantInformationService: ParticipantInformationService,
        private contactInformationService: ContactInformationService,
        private dailySummaryService: DailySummaryService,
        private fitbitWatchService: FitbitWatchService
    ) {}

    public get():Promise<Participant> {
        return this.getParticipant()
        .then((participant) => {
            this.participant.next(participant);
            return participant;
        });
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
        })
        .then((participant) => {
            this.participant.next(participant);
            return true;
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
            this.participantInformationService.getDateEnrolled(),
            this.getBaselineComplete()
        ])
        .then((results) => {
            const participant = new Participant();
            participant.isSetup = results[0];
            participant.staff = results[1];
            participant.name = results[2];
            participant.dateEnrolled = results[3];
            participant.isBaselineComplete = results[4];
            return participant
        });
    }

    private getProfileComplete(): Promise<boolean> {
        return this.isOnboardComplete()
        .then((isComplete) => {
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
        return this.getStaffStatus()
        .then((isStaff) => {
            if (isStaff) {
                return true;
            } else {
                return this.dailySummaryService.getAll()
                .then((summaries) => {
                    return this.participantInformationService.getBaselinePeriod()
                    .then((baselineDays) => {
                        let days_worn = 0;
                        summaries.forEach((summary) => {
                            if(summary.wore_fitbit) {
                                days_worn += 1;
                            }
                        });
                        if (days_worn >= baselineDays) {
                            return true;
                        } else {
                            return false;
                        }
                    })
                });                    
            }
        })
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

    public markOnboardComplete(): Promise<void> {
        return this.storage.set('onboard-complete', true);
    }

    public isOnboardComplete(): Promise<boolean> {
        return this.storage.get('onboard-complete')
        .then(() => {
            return true;
        })
        .catch(() => {
            return false;
        });
    }
}
