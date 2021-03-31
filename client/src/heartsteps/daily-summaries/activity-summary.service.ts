import { Injectable } from "@angular/core";
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
        return Promise.resolve(undefined);
    }

    public updateStatistics(): Promise<void> {
        return this.heartstepsServer.get('activity/summary')
        .then((data) => {
            this.storage.set('activity-summary', data);
            return this.load();
        });


        return this.dailySummaryService.getAll()
        .then((dailySummaries) => {
            let totalActivitiesCompleted = 0;
            let totalActivityMinutes = 0;
            let totalMiles = 0;
            let totalSteps = 0;

            dailySummaries.forEach((summary) => {
                totalActivitiesCompleted += summary.activitiesCompleted;
                totalActivityMinutes += summary.minutes;
                totalMiles += summary.miles;
                totalSteps += summary.steps;
            });

            this.totalActivitiesCompleted.next(totalActivitiesCompleted);
            this.totalActivityMinutes.next(totalActivityMinutes);
            this.totalMiles.next(totalMiles);
            this.totalSteps.next(totalSteps);

            return undefined;
        })
    }

}
