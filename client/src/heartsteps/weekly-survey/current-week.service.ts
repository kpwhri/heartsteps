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
            return week.getDays();
        })
    }

    public load():Promise<Week> {
        return this.storage.get(storageKey)
        .then((data) => {
            const week:Week = this.weekService.deserializeWeek(data);
            if(week.end < new Date()) {
                return Promise.reject("Past end of week");
            } else {
                return Promise.resolve(week);
            }
        })
        .catch(() => {
            return this.update();
        });
    }

    public update():Promise<Week> {
        return this.weekService.getCurrentWeek()
        .then((week:Week) => {
            return this.set(week);
        });
    }

    public set(week:Week):Promise<Week> {
        return this.storage.set(
            storageKey,
            this.weekService.serializeWeek(week)
        )
        .then(() => {
            this.week.next(week);
            return Promise.resolve(week);
        });
    }

}