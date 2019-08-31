import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { DailySummaryService } from "./daily-summary.service";



@Injectable()
export class ActivitySummaryService {

    public totalActivityMinutes: BehaviorSubject<number>;
    public totalActivitiesCompleted: BehaviorSubject<number>;
    public totalMiles: BehaviorSubject<number>;
    public totalSteps: BehaviorSubject<number>;

    constructor(
        private dailySummaryService: DailySummaryService
    ) {
        this.totalActivitiesCompleted = new BehaviorSubject(undefined);
        this.totalActivityMinutes = new BehaviorSubject(undefined);
        this.totalMiles = new BehaviorSubject(undefined);
        this.totalSteps = new BehaviorSubject(undefined);

        this.updateStatistics();
        this.dailySummaryService.updated.subscribe(() => {
            this.updateStatistics();
        });
    }

    public updateStatistics(): Promise<void> {
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
