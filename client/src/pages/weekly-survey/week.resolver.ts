import { Injectable } from "@angular/core";
import { Resolve, ActivatedRouteSnapshot } from "@angular/router";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { WeekService } from "@heartsteps/weekly-survey/week.service";


@Injectable()
export class WeekResolver implements Resolve<Week> {

    constructor(
        private weekService:WeekService
    ){}

    resolve(route:ActivatedRouteSnapshot) {
        return this.weekService.getWeek(route.paramMap.get('weekId'))
    }
}
