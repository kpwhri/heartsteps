import { Injectable } from "@angular/core";
import { Resolve, ActivatedRouteSnapshot } from "@angular/router";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { CurrentWeekService } from "@heartsteps/weekly-survey/current-week.service";


@Injectable()
export class CurrentWeekResolver implements Resolve<Week> {

    constructor(
        private currentWeekService:CurrentWeekService
    ){}

    resolve(route:ActivatedRouteSnapshot) {
        return this.currentWeekService.load();
    }
}
