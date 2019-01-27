import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { DocumentStorageService, DocumentStorage } from "@infrastructure/document-storage.service";
import { ActivityLogService } from "@heartsteps/activity-logs/activity-log.service";
import { CurrentWeekService } from "@heartsteps/weekly-survey/current-week.service";


@Injectable()
export class CurrentActivityLogService {

    public activityLogs: BehaviorSubject<Array<ActivityLog>> = new BehaviorSubject([]);
    public goal: BehaviorSubject<Array<number>> = new BehaviorSubject(null);

    private activityLogStore: DocumentStorage;

    constructor(
        private storage: DocumentStorageService,
        private currentWeekService: CurrentWeekService,
        private activityLogService: ActivityLogService
    ) {
        this.activityLogStore = this.storage.create('activity-logs');

        this.currentWeekService.week.subscribe((week) => {
            this.refreshActivityLogs(week.start, week.end);
        });

        this.activityLogService.created.subscribe((activityLog: ActivityLog) => {
            this.activityLogStore.set(activityLog.id, this.activityLogService.serialize(activityLog))
            .then(() => {
                this.loadActivityLogs();
            });
        });

        this.activityLogService.deleted.subscribe((activityLog: ActivityLog) => {
            this.activityLogStore.remove(activityLog.id)
            .then(() => {
                this.loadActivityLogs();
            })
        });
    }

    private loadActivityLogs(): Promise<Array<ActivityLog>> {
        return this.activityLogStore.getList()
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

    private refreshActivityLogs(start: Date, end: Date): Promise<Array<ActivityLog>> {
        return this.activityLogService.get(start, end)
        .then((logs) => {
            const logObj: any = {};
            logs.forEach((log) => {
                logObj[log.id] = this.activityLogService.serialize(log);
            })
            return this.activityLogStore.setAll(logObj);
        })
        .then(() => {
            return this.loadActivityLogs();
        })
    }

}
