import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { DailySummary } from "./daily-summary.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";

@Injectable()
export class DailySummaryFactory {

    constructor(
        private heartstepsServer: HeartstepsServer
    ) {}

    public date(date: Date):Subject<DailySummary> {
        const day = new Subject<DailySummary>();
        const dateFormatted:string = moment(date).format('YYYY-MM-DD');
        this.heartstepsServer.get(`/activity/summary/${dateFormatted}`)
        .then((response:any) => {
            const summary:DailySummary = new DailySummary();
            summary.moderateMinutes = response.moderate_minutes;
            summary.vigorousMinutes = response.vigorous_minutes;
            summary.totalMinutes = response.total_minutes;
            summary.totalSteps = response.step_count;
            day.next(summary);
        });
        return day;
    }

}