import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { Router } from "@angular/router";


@Injectable()
export class WeeklySurveyService {

    public currentPage:BehaviorSubject<string>;
    private pageIndex:number = 0;
    public pages:Array<string> = ['start', 'survey', 'goal', 'review'];

    private week:any;

    constructor(
        private router:Router
    ){
        this.currentPage = new BehaviorSubject(null);
    }

    loadWeek(weekId:string):Promise<any> {
        this.week = {
            id: weekId,
            start: new Date(),
            end: new Date(),
            goal: 42
        };

        this.currentPage.next(this.pages[0]);
        
        return Promise.resolve(this.week);
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
        this.router.navigate(['weekly-survey', this.week.id, page]);
        this.pageIndex = this.pages.indexOf(page);
        this.currentPage.next(page);
    }

    finish() {
        this.router.navigate(['']);
    }
}
