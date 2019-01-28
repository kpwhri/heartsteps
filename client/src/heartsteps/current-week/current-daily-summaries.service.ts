import { Injectable } from "@angular/core";
import { DailySummaryService } from "@heartsteps/daily-summaries/daily-summary.service";
import { BehaviorSubject } from "rxjs";
import { DailySummary } from "@heartsteps/daily-summaries/daily-summary.model";
import { CurrentActivityLogService } from "./current-activity-log.service";

@Injectable()
export class CurrentDailySummariesService {

    public today: BehaviorSubject<DailySummary> = new BehaviorSubject(undefined);
    public week: BehaviorSubject<Array<DailySummary>> = new BehaviorSubject([]);

    constructor(
        private dailySummaryService: DailySummaryService,
        private currentActivityLogService: CurrentActivityLogService
    ) {
        this.today.next(new DailySummary())
        this.currentActivityLogService.activityLogs
        .filter((logs) => logs !== undefined)
        .subscribe((logs) => {
            const dailySummary = new DailySummary();
            logs.forEach((log) => {
                dailySummary.totalMinutes += log.earnedMinutes;
                if(log.vigorous) {
                    dailySummary.vigorousMinutes += log.duration;
                } else {
                    dailySummary.moderateMinutes += log.duration;
                }
            });
            this.today.next(dailySummary);
        });
    }

}
