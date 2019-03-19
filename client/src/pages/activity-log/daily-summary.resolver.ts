import { Injectable } from "@angular/core";
import { Resolve, ActivatedRouteSnapshot } from "@angular/router";
import { DailySummaryService } from "@heartsteps/daily-summaries/daily-summary.service";
import { DailySummary } from "@heartsteps/daily-summaries/daily-summary.model";
import * as moment from 'moment';

@Injectable()
export class DailySummaryResolver implements Resolve<DailySummary> {

    constructor(
        private dailySummaryService: DailySummaryService
    ){}

    resolve(route:ActivatedRouteSnapshot) {
        const date: Date = moment(route.paramMap.get('date'), 'YYYY-MM-DD').toDate();
        return this.dailySummaryService.get(date)
    }
}
