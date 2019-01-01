import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { WeekService } from "./week.service";
import { BehaviorSubject } from "rxjs";
import { Week } from "./week.model";

const storageKey = 'current-week';

@Injectable()
export class CurrentWeekService {

    public week:BehaviorSubject<Week>;

    constructor(
        private storage:StorageService,
        private weekService:WeekService
    ){
        this.week = new BehaviorSubject(null);
        this.load();
    }

    public getDays():Promise<Array<Date>> {
        return this.load()
        .then((week:Week) => {
            const days:Array<Date> = [];
            let _date:Date = week.start;
            while(_date <= week.end) {
                days.push(_date);
                _date = moment(_date).add(1, 'days').toDate();
            }
            return days;
        })
    }

    public load():Promise<Week> {
        return this.storage.get(storageKey)
        .then((data) => {
            const week:Week = new Week(this.weekService);
            week.id = data.id;
            week.start = data.start;
            week.end = data.end;
            week.goal = data.goal;
            week.confidence = data.confidence;
            this.week.next(week);
            return week;
        })
    }

    public update():Promise<Week> {
        return this.weekService.getCurrentWeek()
        .then((week:Week) => {
            return this.set(week);
        });
    }

    public set(week:Week):Promise<Week> {
        return this.storage.set(storageKey, {
            id: week.id,
            start: week.start,
            end: week.end,
            goal: week.goal,
            confidence: week.confidence
        })
        .then(() => {
            this.week.next(week);
            return Promise.resolve(week);
        });
    }

}