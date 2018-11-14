import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { Subject } from 'rxjs';
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";

export class WeeklyProgressSummary {
    public goal: number;
    public completed: number;
}

@Injectable()
export class WeeklyProgressService {

    constructor(
        private heartstepsServer:HeartstepsServer
    ) {}

    getSummary(start:Date, end:Date): Subject<WeeklyProgressSummary> {
        const weekSummary = new Subject<WeeklyProgressSummary>();
        const startFormatted = moment(start).format('YYYY-MM-DD');
        const endFormatted = moment(end).format('YYYY-MM-DD');
        this.heartstepsServer.get(`activity/summary/${startFormatted}/${endFormatted}`)
        .then((daySummaries:Array<any>) => {
            const summary = new WeeklyProgressSummary();
            summary.goal = 150;
            summary.completed = 0;
            daySummaries.forEach((day:any) => {
                summary.completed += day.total_minutes;
            });
            weekSummary.next(summary);
        });
        return weekSummary;
    }
}