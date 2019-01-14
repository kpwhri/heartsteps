import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { WeekService } from "./week.service";
import { BehaviorSubject } from "rxjs";
import { Week } from "./week.model";

const storageKey = 'current-week';

@Injectable()
export class CurrentWeekService {

    public week:BehaviorSubject<Week> = new BehaviorSubject(null);

    constructor(
        private storage:StorageService,
        private weekService:WeekService
    ) {}

    public getDays():Promise<Array<Date>> {
        return this.load()
        .then((week:Week) => {
            return week.getDays();
        })
    }

    public load():Promise<Week> {
        return this.storage.get(storageKey)
        .then((data) => {
            console.log(data);
            const week:Week = this.weekService.deserializeWeek(data);
            if(week.end < new Date()) {
                return Promise.reject("Past end of week");
            } else {
                this.week.next(week);
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
        })
        .catch(() => {
            return Promise.reject("No current week");
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