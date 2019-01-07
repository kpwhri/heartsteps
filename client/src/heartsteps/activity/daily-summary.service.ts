import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { DailySummary } from "./daily-summary.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { StorageService } from '@infrastructure/storage.service';

const storageKey = 'heartsteps-activity-daily-summaries';
const updateTimeKey = 'heartsteps-activity-daily-update';
const dateFormat = 'YYYY-MM-DD';

@Injectable()
export class DailySummaryService {

    public today: BehaviorSubject<DailySummary>;
    public summaries: BehaviorSubject<Array<DailySummary>>;
    public updateTime: BehaviorSubject<Date>;

    constructor(
        private heartstepsServer: HeartstepsServer,
        private storage: StorageService
    ) {
        this.summaries = new BehaviorSubject([]);
        this.updateTime = new BehaviorSubject(null);
        this.today = new BehaviorSubject(null);
        
        this.storage.get(storageKey)
        .then((summaries:Array<DailySummary>) => {
            this.summaries.next(summaries);
        })
        .catch(() => {
            console.log("No saved summaries");
        });
        this.storage.get(updateTimeKey)
        .then((date:Date) => {
            this.updateTime.next(date);
        })
        .catch(() => {
            console.log("No saved summaries");
        })
    }

    private deserializeSummary(response:any):DailySummary {
        const summary:DailySummary = new DailySummary();
        summary.date = response.date;
        summary.updated = new Date();
        summary.moderateMinutes = response.moderateMinutes;
        summary.vigorousMinutes = response.vigorousMinutes;
        summary.totalMinutes = response.minutes;
        summary.totalSteps = response.steps;
        return summary;
    }

    private setUpdateTime() {
        const updateTime:Date = new Date();
        this.storage.set(updateTimeKey, updateTime)
        .then(() => {
            this.updateTime.next(updateTime);
        });
    }

    public formatDate(date:Date):string {
        return moment(date).format(dateFormat);
    }

    public getDate(date: Date):Promise<DailySummary> {
        const dateFormatted:string = moment(date).format(dateFormat);
        return this.heartstepsServer.get(`/activity/summary/${dateFormatted}`)
        .then((response:any) => {
            this.setUpdateTime();
            const summary = this.deserializeSummary(response);
            return this.updateSummaries([summary])
            .then(() => {
                return summary;
            });
        });
    }

    public getWeek(start: Date, end:Date):Promise<Array<DailySummary>> {
        const startFormatted = moment(start).format('YYYY-MM-DD');
        const endFormatted = moment(end).format('YYYY-MM-DD');
        return this.heartstepsServer.get(`activity/summary/${startFormatted}/${endFormatted}`)
        .then((response:Array<any>) => {
            const summaries:Array<DailySummary> = [];
            response.forEach((res)=> {
                summaries.push(this.deserializeSummary(res));
            })
            return this.updateSummaries(summaries)
            .then(() => {
                return summaries;
            });
        });
    }

    private updateSummaries(newSummaries:Array<DailySummary>):Promise<boolean> {
        return this.storage.get(storageKey)
        .catch(() => {
            return [];
        })
        .then((summaries:any) => {
            newSummaries.forEach((summary:DailySummary) => {
                let found = false;
                summaries.forEach((existingSummary:DailySummary, index:number) => {
                    if(existingSummary.date == summary.date) {
                        summaries[index] = summary;
                        found = true;
                    }
                });
                if(!found) {
                    summaries.push(summary);
                }
            });
            return this.storage.set(storageKey, summaries);
        })
        .then((summaries) => {
            this.summaries.next(summaries);
            return true;
        });
    }

}