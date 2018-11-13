import { Injectable } from "@angular/core";
import { ActivityLogService } from "./activity-log.service";
import { Subject } from "rxjs";
import { DailySummary } from "./daily-summary.model";



@Injectable()
export class DailySummaryFactory {

    constructor(
        private activityLogService: ActivityLogService
    ) {}

    public date(date: Date):Subject<DailySummary> {
        const day = new Subject<DailySummary>();
        this.activityLogService.getSummary(date)
        .then((summary:DailySummary) => {
            day.next(summary);
        })
        return day;
    }

}