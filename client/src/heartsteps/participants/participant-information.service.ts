import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { StorageService } from "@infrastructure/storage.service";

import * as moment from 'moment';

export class StudyContactInformation {
    name: string;
    number: string;
}

@Injectable()
export class ParticipantInformationService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private storage: StorageService
    ) {}

    public load(): Promise<boolean> {
        return this.heartstepsServer.get('information')
            .then((data) => {
                console.log("ParticipantInformationService.load()", JSON.stringify(data))
            return Promise.all([
                this.setDateEnrolled(data['date_enrolled']),
                this.setStaff(data['staff']),
                this.setBaselinePeriod(data['baselinePeriod']),
                this.setStudyContactInformation(data['studyContactName'], data['studyContactNumber']),
                this.setBaselineComplete(data['baselineComplete']),
                this.setParticipantTags(data['participantTags'])
            ])
        })
        .then(() => {
            return true;
        });
    }

    public isStaff(): Promise<boolean> {
        return this.getStaff()
        .then((isStaff: boolean) => {
            if(isStaff) {
                return Promise.resolve(true);
            } else {
                return Promise.reject('Not staff');
            }
        })
        .catch(() => {
            return Promise.reject('Not staff');
        })
    }

    private setDateEnrolled(enrolled_date_string: string): Promise<boolean> {
        return this.storage.set('date_enrolled', enrolled_date_string)
        .then(() => {
            return true;
        });
    }

    public getDateEnrolled(): Promise<Date> {
        return this.storage.get('date_enrolled')
        .catch(() => {
            return this.load()
            .then(() => {
                return this.storage.get('date_enrolled');
            })
        })
        .then((date_enrolled_string) => {
            return moment(date_enrolled_string, "YYYY-MM-DD").toDate();
        });
    }

    private setStaff(isStaff: boolean): Promise<boolean> {
        return this.storage.set('isStaff', isStaff)
        .then(() => {
            return true;
        });
    }

    private getStaff(): Promise<boolean> {
        return this.storage.get('isStaff')
        .then((isStaff) => {
            return isStaff;
        })
        .catch(() => {
            return Promise.reject('No data');
        });
    }

    private setBaselinePeriod(baselinePeriod: number): Promise<boolean> {
        return this.storage.set('baselinePeriod', baselinePeriod)
        .then(() => {
            return true;
        });
    }

    public getBaselinePeriod(): Promise<number> {
        return this.storage.get('baselinePeriod')
        .then((baselinePeriod) => {
            return baselinePeriod
        });
    }

    private setStudyContactInformation(name: string, number: string): Promise<boolean> {
        return this.storage.set('studyContactInformation', {
            name: name,
            number: number
        })
        .then(() => {
            return true;
        });
    }

    public getStudyContactInformation(): Promise<StudyContactInformation> {
        return this.storage.get('studyContactInformation')
        .then((info) => {
            const contactInfo = new StudyContactInformation()
            contactInfo.name = info.name;
            contactInfo.number = info.number
            return contactInfo;
        })
    }

    private setBaselineComplete(isBaselineComplete: boolean): Promise<void> {
        return this.storage.set('baselineComplete', isBaselineComplete)
        .then(() => {
            return undefined;
        });
    }

    public getBaselineComplete():Promise<boolean> {
        return this.storage.get('baselineComplete')
        .then((baselineComplete) => {
            return baselineComplete;
        })
        .catch(() => {
            return false;
        });
    }
    private setParticipantTags(participantTags: string[]): Promise<boolean> {
        return this.storage.set('participantTags', participantTags)
        .then(() => {
            return true;
        });
    }

    public getParticipantTags():Promise<string[]> {
        return this.load()
                .then(() => {
                    return this.storage.get('participantTags');
                })       
    }
}
