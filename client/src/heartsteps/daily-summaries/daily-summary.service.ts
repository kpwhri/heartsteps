import { Injectable, EventEmitter } from "@angular/core";
import { DailySummary } from "./daily-summary.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { DailySummarySerializer } from "./daily-summary.serializer";
import { Subscribable } from "rxjs/Observable";
import {
    DocumentStorage,
    DocumentStorageService,
} from "@infrastructure/document-storage.service";
import { BehaviorSubject } from "rxjs";
import * as moment from "moment";
import { ActivityLogService } from "@heartsteps/activity-logs/activity-log.service";
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { DateFactory } from "@infrastructure/date.factory";

@Injectable()
export class DailySummaryService {
    public updated: EventEmitter<DailySummary> = new EventEmitter();

    private storage: DocumentStorage;
    private cacheStartDate: Date;

    constructor(
        private activityLogService: ActivityLogService,
        private heartstepsServer: HeartstepsServer,
        private serializer: DailySummarySerializer,
        private dateFactory: DateFactory,
        storageService: DocumentStorageService
    ) {
        console.log("DailySummaryService.constructor() point 1");
        this.storage = storageService.create("daily-summaries");
        console.log("DailySummaryService.constructor() point 2");
        this.activityLogService.updated.subscribe(
            (activityLog: ActivityLog) => {
                console.log("DailySummaryService.constructor() point 3");
                this.update(activityLog.start);
            }
        );
        this.activityLogService.deleted.subscribe(
            (activityLog: ActivityLog) => {
                console.log("DailySummaryService.constructor() point 4");
                this.update(activityLog.start);
            }
        );
    }

    public setup(cacheStartDate?: Date): Promise<void> {
        this.cacheStartDate = cacheStartDate;

        return this.cleanCache()
            .then(() => {
                return Promise.all([
                    this.getDatesToStore(),
                    this.storage.getIds(),
                ]);
            })
            .then((results) => {
                const datesToStore: Array<Date> = results[0];
                const storedIds: Array<String> = results[1];
                const datesToUpdate = datesToStore.filter((date) => {
                    const serializedDate = this.serializer.formatDate(date);
                    if (storedIds.indexOf(serializedDate) === -1) {
                        return true;
                    } else {
                        return false;
                    }
                });
                if (datesToUpdate.length >= 3) {
                    return this.reload();
                } else {
                    return this.loadDates(datesToUpdate);
                }
            })
            .then(() => {
                return Promise.resolve(undefined);
            });
    }

    public reload(dates?: Array<Date>): Promise<void> {
        if (!dates) {
            dates = this.getDatesToStore();
        }
        dates.sort(function (a, b) {
            if (a > b) return 1;
            if (a < b) return -1;
            return 0;
        });
        return this.storage
            .destroy()
            .then(() => {
                return this.loadRange(dates.shift(), dates.pop());
            })
            .then((summaries) => {
                summaries.forEach((summary) => {
                    this.updated.emit(summary);
                });
                return undefined;
            });
    }

    public get(date: Date): Promise<DailySummary> {
        return this.retrieve(date).catch(() => {
            return this.loadDate(date).then((summary) => {
                this.updated.emit(summary);
                return summary;
            });
        });
    }

    public getRange(start: Date, end: Date): Promise<Array<DailySummary>> {
        return this.loadRange(start, end).then((summaries) => {
            summaries.forEach((summary) => {
                this.updated.emit(summary);
            });
            return summaries;
        });
    }

    public updateFromFitbit(date: Date): Promise<DailySummary> {
        console.log("DailySummaryService.updateFromFitbit() - point 1");
        const dateFormatted = this.serializer.formatDate(date);
        console.log(
            "DailySummaryService.updateFromFitbit() - point 2: date=",
            date
        );
        return this.heartstepsServer
            .get(`activity/summary/update/${dateFormatted}`)
            .then((data) => {
                console.log(
                    "DailySummaryService.updateFromFitbit() - point 3: data=",
                    data
                );
                const summary = this.serializer.deserialize(data);
                console.log(
                    "DailySummaryService.updateFromFitbit() - point 4: summary=",
                    summary
                );
                return this.store(summary);
            })
            .then((summary) => {
                console.log(
                    "DailySummaryService.updateFromFitbit() - point 5: summary.date=",
                    summary.date
                );
                this.updated.emit(summary);
                console.log("DailySummaryService.updateFromFitbit() - point 6");
                return summary;
            });
    }

    public update(date: Date): Promise<DailySummary> {
        console.log("DailySummaryService.update() point 1");
        return this.loadDate(date).then((summary) => {
            console.log("DailySummaryService.update() point 1");
            this.updated.emit(summary);
            console.log("DailySummaryService.update() point 1");
            return summary;
        });
    }

    public updateCurrentWeek(): Promise<Array<DailySummary>> {
        const currentWeek = this.dateFactory.getCurrentWeek();
        return this.loadRange(
            currentWeek[0],
            currentWeek[currentWeek.length - 1]
        ).then((summaries) => {
            summaries.forEach((summary) => {
                this.updated.emit(summary);
            });
            return summaries;
        });
    }

    public watch(date: Date): Subscribable<DailySummary> {
        const dailySummarySubject: BehaviorSubject<DailySummary> =
            new BehaviorSubject(undefined);

        this.get(date).then((summary) => {
            dailySummarySubject.next(summary);
        });

        this.updated.subscribe((summary) => {
            if (summary.isDate(date)) {
                dailySummarySubject.next(summary);
            }
        });

        return dailySummarySubject.filter((summary) => summary !== undefined);
    }

    public watchRange(
        start: Date,
        end: Date
    ): Subscribable<Array<DailySummary>> {
        const weekSummarySubject: BehaviorSubject<Array<DailySummary>> =
            new BehaviorSubject([]);

        this.retrieveRange(start, end)
            .catch(() => {
                return this.getRange(start, end);
            })
            .then((summaries) => {
                weekSummarySubject.next(summaries);
            });

        this.updated.subscribe((summary: DailySummary) => {
            if (moment(summary.date).isBetween(start, end, "day", "[]")) {
                this.retrieveRange(start, end).then((summaries) => {
                    weekSummarySubject.next(summaries);
                });
            }
        });

        return weekSummarySubject;
    }

    public getAll(): Promise<Array<DailySummary>> {
        return this.storage.getList().then((items) => {
            return items.map((data) => {
                return this.serializer.deserialize(data);
            });
        });
    }

    private retrieve(date: Date): Promise<DailySummary> {
        return this.storage
            .get(this.serializer.formatDate(date))
            .then((data) => {
                return this.serializer.deserialize(data);
            });
    }

    private retrieveRange(
        start: Date,
        end: Date
    ): Promise<Array<DailySummary>> {
        return this.storage
            .getList()
            .then((items) => {
                return items.map((data) => {
                    return this.serializer.deserialize(data);
                });
            })
            .then((summaries) => {
                return summaries.filter((summary) => {
                    const summaryMoment = moment(summary.date);
                    const isBeforeStart = summaryMoment.isBefore(start, "day");
                    const isAfterEnd = summaryMoment.isAfter(end, "day");
                    if (!isBeforeStart && !isAfterEnd) {
                        return true;
                    } else {
                        return false;
                    }
                });
            });
    }

    private store(summary: DailySummary): Promise<DailySummary> {
        const serialized = this.serializer.serialize(summary);
        return this.storage.set(serialized["date"], serialized).then(() => {
            return summary;
        });
    }

    private cleanCache(): Promise<undefined> {
        this.storage.getAll().then((data) => {
            const newData = {};
            this.getDatesToStore().forEach((date) => {
                const date_string = this.serializer.formatDate(date);
                if (data[date_string]) {
                    newData[date_string] = data[date_string];
                }
            });
            return this.storage.setAll(newData);
        });
        return Promise.resolve(undefined);
    }

    private getDatesToStore(): Array<Date> {
        if (this.cacheStartDate) {
            return this.dateFactory.getDatesFrom(this.cacheStartDate);
        } else {
            return this.dateFactory.getCurrentWeek();
        }
    }

    private loadDates(dates: Array<Date>): Promise<void> {
        let promise = Promise.resolve();
        dates.forEach((date) => {
            promise = promise.then(() => {
                return this.get(date).then(() => {
                    return Promise.resolve(undefined);
                });
            });
        });
        return promise;
    }

    private loadDate(date: Date): Promise<DailySummary> {
        const dateFormatted = this.serializer.formatDate(date);
        return this.heartstepsServer
            .get(`activity/summary/${dateFormatted}`)
            .then((data) => {
                const summary = this.serializer.deserialize(data);
                return this.store(summary);
            });
    }

    private loadRange(start: Date, end: Date): Promise<Array<DailySummary>> {
        const startFormatted = this.serializer.formatDate(start);
        const endFormatted = this.serializer.formatDate(end);
        return this.heartstepsServer
            .get(`activity/summary/${startFormatted}/${endFormatted}`)
            .then((response: Array<any>) => {
                const summaries: Array<DailySummary> = [];
                let promise = Promise.resolve();

                response.forEach((item) => {
                    const summary = this.serializer.deserialize(item);
                    summaries.push(summary);

                    promise = promise.then(() => {
                        return this.store(summary).then(() => {
                            return undefined;
                        });
                    });
                });
                return promise.then(() => {
                    return summaries;
                });
            });
    }
}
