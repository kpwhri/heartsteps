import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { Week } from "@heartsteps/weekly-survey/week.model";


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
