import { Injectable } from "@angular/core";
// tslint:disable-next-line:no-unused-variable
import { DocumentStorage, DocumentStorageService } from "@infrastructure/document-storage.service";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { StorageService } from "@infrastructure/storage.service";
import { BehaviorSubject } from "rxjs";
import { DailySummaryService } from "./daily-summary.service";


@Injectable()
export class ActivitySummaryService {

    public totalActivityMinutes: BehaviorSubject<number>;
    public totalActivitiesCompleted: BehaviorSubject<number>;
    public totalMiles: BehaviorSubject<number>;
    public totalSteps: BehaviorSubject<number>;


    constructor(
        private dailySummaryService: DailySummaryService,
        private storage: StorageService,
        private heartstepsServer: HeartstepsServer
    ) {
        this.totalActivitiesCompleted = new BehaviorSubject(undefined);
        this.totalActivityMinutes = new BehaviorSubject(undefined);
        this.totalMiles = new BehaviorSubject(undefined);
        this.totalSteps = new BehaviorSubject(undefined);

        var updateDebounce = undefined;
        this.dailySummaryService.updated.subscribe(() => {
            if (updateDebounce) clearTimeout(updateDebounce);
            updateDebounce = setTimeout(() => {
                this.updateStatistics();
            }, 500);
        });
    }

    private get(): Promise<void> {
        return this.heartstepsServer.get('activity/summary')
        .then((data) => {
            this.storage.set('activity-summary', data);
            return undefined;
        });
    }

    private load(): Promise<void> {
        return this.storage.get('activity-summary')
        .then((data) => {
            this.totalActivitiesCompleted.next(data['activities_completed']);
            this.totalActivityMinutes.next(data['minutes']);
            this.totalMiles.next(data['minutes']);
            this.totalSteps.next(data['steps']);
        })
        .catch(() => {
            this.get()
            .then(() => {
                this.load()
            });
        });
    }

    public updateStatistics(): Promise<void> {
        return this.heartstepsServer.get('activity/summary')
        .then((data) => {
            this.storage.set('activity-summary', data);
            return this.load();
        });
    }

}
