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
        return this.getWeeks(route.paramMap.get('weekId'));
    }

    private getWeeks(weekId:string):Promise<any> {
        return this.weekService.getWeek(weekId)
        .then((week:Week) => {
            return this.weekService.getWeekAfter(week)
            .then((nextWeek:Week) => {
                return [
                    week,
                    nextWeek
                ];
            })
            .catch(() => {
                return [
                    week
                ];
            });
        });
    }
}
