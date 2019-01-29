import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { DocumentStorageService, DocumentStorage } from "@infrastructure/document-storage.service";
import { ActivityLogService } from "@heartsteps/activity-logs/activity-log.service";
import { CurrentWeekService } from "./current-week.service";

@Injectable()
export class CurrentActivityLogService {

    public activityLogs: BehaviorSubject<Array<ActivityLog>> = new BehaviorSubject(undefined);
    
    private storage: DocumentStorage;

    constructor(
        documentStorageService: DocumentStorageService,
        private activityLogService: ActivityLogService,
        private currentWeekService: CurrentWeekService
    ) {
        this.storage = documentStorageService.create('activity-logs');
        this.load();

        this.activityLogService.updated.subscribe((activityLog: ActivityLog) => {
            this.storage.set(activityLog.id, this.activityLogService.serialize(activityLog))
            .then(() => {
                this.load();
            });
        });

        this.activityLogService.deleted.subscribe((activityLog: ActivityLog) => {
            this.storage.remove(activityLog.id)
            .then(() => {
                this.load();
            })
        });
    }

    private load(): Promise<Array<ActivityLog>> {
        return this.storage.getList()
        .then((items) => {
            return items.map((data) => {
                return this.activityLogService.deserialize(data);
            });
        })
        .then((logs) => {
            this.activityLogs.next(logs);
            return logs;
        });
    }

    public update(): Promise<Array<ActivityLog>> {
        return this.currentWeekService.get()
        .then((week) => {
            return this.activityLogService.get(week.start, week.end)
        })
        .then((logs) => {
            const logObj: any = {};
            logs.forEach((log) => {
                logObj[log.id] = this.activityLogService.serialize(log);
            })
            return this.storage.setAll(logObj);
        })
        .then(() => {
            return this.load();
        })
    }

}
