import { Component, OnInit, OnDestroy } from "@angular/core";
import { Router, ActivatedRoute, NavigationEnd } from "@angular/router";
import { Subscription } from "rxjs";
import { WeeklySurveyService } from "./weekly-survey.service";
import { Week } from "@heartsteps/weekly-survey/week.model";

@Component({
    templateUrl: './weekly-survey.page.html'
})
export class WeeklySurveyPage implements OnInit, OnDestroy {

    pageSubscription: Subscription;
    pages:Array<string>;
    activePage:string;
    firstPage: boolean;
    title:string;

    week:Week;

    constructor(
        private weeklySurveyService: WeeklySurveyService,
        private activatedRoute: ActivatedRoute,
        private router: Router
    ) {}

    ngOnInit() {
        this.week = this.activatedRoute.snapshot.data['weeks'][0];
        this.weeklySurveyService.week = this.week;
        this.weeklySurveyService.nextWeek = this.activatedRoute.snapshot.data['weeks'][1];

        this.weeklySurveyService.change.subscribe(() => {
            this.nextPage();
        });

        this.pages = ['start', 'survey', 'goal', 'review'];
        
        this.updatePage();
        this.pageSubscription = this.router.events
        .filter((event) => event instanceof NavigationEnd)
        .subscribe(() => {
            this.updatePage();
        });
    }

    updatePage() {
        this.activePage = this.activatedRoute.snapshot.firstChild.url[0].path;

        switch(this.activePage) {
            case 'survey':
                this.title = "Weekly Questions";
                break;
            case 'goal':
                this.title = "New goal for upcoming week";
                break;
            default:
                this.title = "Weekly Review"
        }

        if(this.pages.indexOf(this.activePage) === 0) {
            this.firstPage = true;
        } else {
            this.firstPage = false;
        }
    }

    finish(){
        this.router.navigate(['/']);
    }

    nextPage() {
        const pageIndex:number = this.pages.indexOf(this.activePage); 
        const nextPage:number = pageIndex + 1;
        if(nextPage >= this.pages.length) {
            this.finish();
        } else {
            this.navigateToPage(this.pages[nextPage]);
        }
    }

    previousPage() {
        const pageIndex:number = this.pages.indexOf(this.activePage); 
        const previousPage: number = pageIndex - 1;
        if(previousPage < 0) {
            this.navigateToPage(this.pages[0]);
        } else {
            this.navigateToPage(this.pages[previousPage]);
        }
    }

    navigateToPage(page:string) {
        this.router.navigate(['weekly-survey', this.week.id, page]);
    }

    ngOnDestroy() {
        if(this.pageSubscription) {
            this.pageSubscription.unsubscribe();
        }
    }



}
