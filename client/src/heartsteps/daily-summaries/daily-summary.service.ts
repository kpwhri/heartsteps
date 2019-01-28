import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { DailySummary } from "./daily-summary.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";

const dateFormat = 'YYYY-MM-DD';

@Injectable()
export class DailySummaryService {

    public today: BehaviorSubject<DailySummary>;
    public summaries: BehaviorSubject<Array<DailySummary>>;
    public updateTime: BehaviorSubject<Date>;

    constructor(
        private heartstepsServer: HeartstepsServer
    ) {
        this.summaries = new BehaviorSubject([]);
        this.updateTime = new BehaviorSubject(null);
        this.today = new BehaviorSubject(null);
    }

    public formatDate(date:Date):string {
        return moment(date).format(dateFormat);
    }

    public getDate(date: Date):Promise<DailySummary> {
        const dateFormatted:string = moment(date).format(dateFormat);
        return this.heartstepsServer.get(`/activity/summary/${dateFormatted}`)
        .then((response:any) => {
            const summary = this.deserializeSummary(response);
            return summary;
        });
    }

    public getWeek(start: Date, end:Date):Promise<Array<DailySummary>> {
        const startFormatted = moment(start).format(dateFormat);
        const endFormatted = moment(end).format(dateFormat);
        return this.heartstepsServer.get(`activity/summary/${startFormatted}/${endFormatted}`)
        .then((response:Array<any>) => {
            const summaries:Array<DailySummary> = [];
            response.forEach((res)=> {
                summaries.push(this.deserializeSummary(res));
            })
            return summaries;
        });
    }

    private deserializeSummary(data:any):DailySummary {
        const summary:DailySummary = new DailySummary();
        summary.date = moment(data.date, dateFormat).toDate();
        summary.updated = new Date();
        summary.moderateMinutes = data.moderateMinutes;
        summary.vigorousMinutes = data.vigorousMinutes;
        summary.totalMinutes = data.minutes;
        summary.totalSteps = data.steps;
        return summary;
    }
}
