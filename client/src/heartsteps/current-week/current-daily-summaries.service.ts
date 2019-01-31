import { Injectable } from "@angular/core";
import { DailySummaryService } from "@heartsteps/daily-summaries/daily-summary.service";
import { BehaviorSubject } from "rxjs";
import { DailySummary } from "@heartsteps/daily-summaries/daily-summary.model";
import { ActivityLogService } from "@heartsteps/activity-logs/activity-log.service";
import { CurrentWeekService } from "./current-week.service";
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { merge } from "rxjs/observable/merge";
import { DocumentStorageService, DocumentStorage } from "@infrastructure/document-storage.service";
import { DailySummarySerializer } from "@heartsteps/daily-summaries/daily-summary.serializer";
import { weekdays } from "moment";

@Injectable()
export class CurrentDailySummariesService {

    public today: BehaviorSubject<DailySummary> = new BehaviorSubject(undefined);
    public week: BehaviorSubject<Array<DailySummary>> = new BehaviorSubject(undefined);

    private storage: DocumentStorage;

    constructor(
        private currentWeekService: CurrentWeekService,
        private dailySummaryService: DailySummaryService,
        private activityLogService: ActivityLogService,
        private dailySummarySerializer: DailySummarySerializer,
        documentStorageService: DocumentStorageService
    ) {
        this.storage = documentStorageService.create('current-daily-summaries')
        this.reload();

        this.dailySummaryService.updated.subscribe((summary:DailySummary) => {
            this.currentWeekService.isWithinWeek(summary.date)
            .then(() => {
                this.set(summary);
                this.reload();
            });
        });

        merge(
            this.activityLogService.updated.asObservable(),
            this.activityLogService.deleted.asObservable()
        ).subscribe((log: ActivityLog) => {
            this.currentWeekService.isWithinWeek(log.start)
            .then(() => {
                this.update(log.start);
            });
        });
    }

    private reload() {
        this.storage.getList()
        .then((items) => {
            if(items.length < 1) {
                return this.updateAll();
            } else {
                const summaries = items.map((data) => {
                    return this.dailySummarySerializer.deserialize(data);
                });
                return summaries;
            }
        })
        .then((summaries) => {
            this.week.next(summaries);
            const today:DailySummary = summaries.find((summary) => summary.isToday());
            this.today.next(today);
        })
        .catch(() => {
            this.updateAll();
        });
    }

    private set(summary: DailySummary): Promise<any> {
        const serialized = this.dailySummarySerializer.serialize(summary);
        return this.storage.set(serialized['date'], serialized);
    }

    private update(date:Date) {
        this.dailySummaryService.get(date)
        .then((summary) => {
            return this.set(summary);
        })
        .then(() => {
            this.reload();
        });
    }

    private updateAll(): Promise<Array<DailySummary>> {
        return this.currentWeekService.get()
        .then((week) => {
            return this.dailySummaryService.getWeek(week.start, week.end);
        })
        .then((summaries) => {
            const obj = {};
            summaries.forEach((summary) => {
                const serialized = this.dailySummarySerializer.serialize(summary);
                obj[serialized['date']] = serialized;
            });
            return this.storage.setAll(obj)
            .then(() => {
                return summaries;
            });
        })
    }

    private serialize() {

    }

    private deserialize() {

    }

}
