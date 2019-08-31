import { Component, OnInit, OnDestroy } from "@angular/core";
import { CachedActivityLogService } from "@heartsteps/activity-logs/cached-activity-log.service";
import { ActivitySummaryService } from "@heartsteps/daily-summaries/activity-summary.service";
import { Subscription } from "rxjs";

@Component({
    templateUrl: './activities.page.html'
})
export class ActivitiesPage implements OnInit, OnDestroy {

    public days: Array<Date>

    public totalActivityTime: string = '--';
    public totalActivitiesComplete: number;
    public totalDistance: string = '--';
    public totalSteps: number;

    private totalActivityTimeSubscription: Subscription;
    private totalActivitiesCompleteSubscription: Subscription;
    private totalMilesSubscription: Subscription;
    private totalStepsSubscription: Subscription;

    constructor(
        private activitySummaryService: ActivitySummaryService,
        private cachedActivityLogService: CachedActivityLogService
    ){
        this.cachedActivityLogService.getCachedDates()
        .then((cachedDates) => {
            this.days = cachedDates.reverse();
            this.cachedActivityLogService.update();
        });
    }

    ngOnInit() {

        this.totalActivitiesCompleteSubscription = this.activitySummaryService.totalActivitiesCompleted
        .filter(activities => activities !== undefined)
        .subscribe((totalActivitiesComplete) => {
            this.totalActivitiesComplete = totalActivitiesComplete;
        });
        this.totalActivityTimeSubscription = this.activitySummaryService.totalActivityMinutes
        .filter(minutes => minutes !== undefined)
        .subscribe((totalActivityMinutes) => {
            const hours = Math.floor(totalActivityMinutes/60);
            const minutes = totalActivityMinutes - (hours * 60);

            this.totalActivityTime = `${hours} hr ${minutes} min`;
        });
        this.totalMilesSubscription = this.activitySummaryService.totalMiles
        .filter(miles => miles !== undefined)
        .subscribe((miles) => {
            this.totalDistance = `${miles} miles`;
        });
        this.totalStepsSubscription = this.activitySummaryService.totalSteps
        .filter(steps => steps !== undefined)
        .subscribe((steps) => {
            this.totalSteps = steps;
        });

    }

    ngOnDestroy() {
        this.totalActivitiesCompleteSubscription.unsubscribe();
        this.totalActivityTimeSubscription.unsubscribe();
        this.totalMilesSubscription.unsubscribe();
        this.totalStepsSubscription.unsubscribe();
    }
    
}
