import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { WeekService } from "@heartsteps/weekly-survey/week.service";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { BehaviorSubject } from "rxjs";

const storageKey = 'current-week';

@Injectable()
export class CurrentWeekService {

    public week: BehaviorSubject<Week> = new BehaviorSubject(undefined);

    constructor(
        private storage:StorageService,
        private weekService:WeekService
    ) {}

    public setUp() {
        this.load()
        .then((week) => {
            this.week.next(week);
        });
    }

    public isWithinWeek(date: Date): Promise<boolean> {
        return this.get()
        .then((week) => {
            if(date >= week.start && date <= week.end) {
                return Promise.resolve(true);
            } else {
                return Promise.reject('Not within week');
            }
        })
    }

    public get():Promise<Week> {
        return this.storage.get(storageKey)
        .then((data) => {
            return this.weekService.deserializeWeek(data)
        })
        .catch(() => {
            return this.update();
        });
    }

    public getDays():Promise<Array<Date>> {
        return this.load()
        .then((week:Week) => {
            return week.getDays();
        })
    }

    public load():Promise<Week> {
        return this.get()
        .then((week) => {
            if(week.end < new Date()) {
                return this.update();
            } else {
                return Promise.resolve(week);
            }
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
