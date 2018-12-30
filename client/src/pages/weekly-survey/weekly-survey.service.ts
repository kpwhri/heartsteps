import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { Router } from "@angular/router";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { WeekService } from "@heartsteps/weekly-survey/week.service";


@Injectable()
export class WeeklySurveyService {

    private pageIndex:number = 0;
    public pages:Array<string> = ['start', 'survey', 'goal', 'review'];

    public week:Week;
    public nextWeek:Week;

    constructor(
        private router:Router,
        private weekService: WeekService
    ){}

    loadWeek(weekId:string):Promise<Week> {
        return this.weekService.getWeek(weekId)
        .then((week:Week) => {
            this.week = week;
            return this.weekService.getWeekAfter(week);
        })
        .then((nextWeek:Week) => {
            this.nextWeek = nextWeek;
            return this.week;
        });
    }

    nextPage() {
        const nextPage:number = this.pageIndex + 1;
        if(nextPage >= this.pages.length) {
            this.finish();
        } else {
            this.navigateToPage(this.pages[nextPage]);
        }
    }

    previousPage() {
        const previousPage: number = this.pageIndex - 1;
        if(previousPage < 0) {
            this.navigateToPage(this.pages[0]);
        } else {
            this.navigateToPage(this.pages[previousPage]);
        }
    }

    navigateToPage(page:string) {
        this.pageIndex = this.pages.indexOf(page);
        this.router.navigate(['weekly-survey', this.week.id, page]);
    }

    finish() {
        this.router.navigate(['']);
    }
}
