import { Injectable } from "@angular/core";
import { BehaviorSubject, Subject } from "rxjs";
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { DocumentStorageService, DocumentStorage } from "@infrastructure/document-storage.service";
import { ActivityLogService } from "@heartsteps/activity-logs/activity-log.service";
import { DateFactory } from "@infrastructure/date.factory";
import * as moment from 'moment';
import { Subscribable } from "rxjs/Observable";
import { ParticipantInformationService } from "@heartsteps/participants/participant-information.service";

@Injectable()
export class CachedActivityLogService {

    public activityLogs: BehaviorSubject<Array<ActivityLog>> = new BehaviorSubject(undefined);
    
    private storage: DocumentStorage;

    constructor(
        private documentStorageService: DocumentStorageService,
        private activityLogService: ActivityLogService,
        private dateFactory: DateFactory,
        private participantInformationService: ParticipantInformationService
    ) {}

    public setup():Promise<boolean> {
        this.storage = this.documentStorageService.create('activity-logs');
        this.activityLogService.updated.subscribe((activityLog: ActivityLog) => {
            this.storage.set(activityLog.id, this.activityLogService.serialize(activityLog))
            .then(() => {
                this.reload();
            });
        });
        this.activityLogService.deleted.subscribe((activityLog: ActivityLog) => {
            this.storage.remove(activityLog.id)
            .then(() => {
                this.reload();
            })
        });

        return this.update()
        .then(() => {
            return true;
        });
    }

    public get(day: Date): Subscribable<Array<ActivityLog>> {
        const daySubject: BehaviorSubject<Array<ActivityLog>> = new BehaviorSubject(undefined);

        this.activityLogs
        .filter(logs => logs !== undefined)
        .subscribe((logs) => {
            const dayLogs = logs.filter((activityLog) => {
                if(this.dateFactory.isSameDay(day, activityLog.start)) {
                    return true;
                } else {
                    return false;
                }
            });
            daySubject.next(dayLogs);
        });

        return daySubject.asObservable();
    }

    public load(start: Date, end: Date): Promise<Array<ActivityLog>> {
        return Promise.resolve([]);
    }

    public getCachedDates(): Promise<Array<Date>> {
        return this.participantInformationService.getDateEnrolled()
        .then((dateEnrolled) => {
            const days = [];
            const today = new Date();
            
            days.push(today);
            this.dateFactory.getCurrentWeek().reverse().forEach((day) => {
                if(moment(day).isBefore(today, 'day') && moment(day).isSameOrAfter(dateEnrolled, 'day')) {
                    days.push(day);
                }
            });
            const dayLastWeek: Date = moment().subtract(7, 'days').toDate();
            this.dateFactory.getWeek(dayLastWeek).reverse().forEach((day) => {
                if(moment(day).isSameOrAfter(dateEnrolled, 'day')) {
                    days.push(day);
                }
            });
    
            return days.reverse();
        })
        .catch(() => {
            return Promise.resolve([]);
        });
    }

    public update(): Promise<Array<ActivityLog>> {
        return this.getCachedDates()
        .then((cachedDates) => {
            const firstDate = cachedDates[0];
            const lastDate = cachedDates[cachedDates.length-1];
            return this.activityLogService.get(firstDate, lastDate)
        })
        .then((logs) => {
            const logObj: any = {};
            logs.forEach((log) => {
                logObj[log.id] = this.activityLogService.serialize(log);
            })
            return this.storage.setAll(logObj);
        })
        .then(() => {
            return this.reload();
        });
    }

    private reload(): Promise<Array<ActivityLog>> {
        return this.storage.getList()
        .then((items) => {
            return items.map((data) => {
                return this.activityLogService.deserialize(data);
            });
        })
        .then((logs) => {
            this.activityLogService.sort(logs);
            this.activityLogs.next(logs);
            return logs;
        });
    }

}
