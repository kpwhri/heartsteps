import { Injectable } from "@angular/core";
import { BehaviorSubject, Observable, Subject } from "rxjs";
import { Router } from "@angular/router";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { WeekService } from "@heartsteps/weekly-survey/week.service";
import { EventEmitter } from "events";
import { Subscribable } from "rxjs/Observable";


@Injectable()
export class WeeklySurveyService {
    public week:Week;
    public nextWeek:Week;

    public change:Subject<boolean>;

    constructor(){
        this.change = new Subject();
    }

    nextPage() {
        this.change.next();
    }

}
