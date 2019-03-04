import { Injectable } from "@angular/core";
import { Resolve, ActivatedRouteSnapshot } from "@angular/router";
import { DailySummary } from "@heartsteps/daily-summaries/daily-summary.model";
import { CurrentDailySummariesService } from "@heartsteps/current-week/current-daily-summaries.service";


@Injectable()
export class CurrentDailySummaryResolver implements Resolve<Array<DailySummary>> {

    constructor(
        private currentDailySummaryService:CurrentDailySummariesService
    ){}

    resolve(route: ActivatedRouteSnapshot) {
        return this.currentDailySummaryService.week
        .filter((value) => value !== undefined)
        .first();
    }
}
