import { Component, OnInit, OnDestroy } from "@angular/core";
import { Router, ActivatedRoute, ParamMap, UrlSegment, NavigationEnd } from "@angular/router";
import { Subscription } from "rxjs";
import { WeeklySurveyService } from "./weekly-survey.service";
import { urlToNavGroupStrings } from "ionic-angular/umd/navigation/url-serializer";

@Component({
    templateUrl: './weekly-survey.page.html'
})
export class WeeklySurveyPage implements OnInit, OnDestroy {

    pageSubscription: Subscription;
    pages:Array<string>;
    activePage:string;
    firstPage: boolean;
    title:string;

    constructor(
        private weeklySurveyService: WeeklySurveyService,
        private activeRoute: ActivatedRoute,
        private router: Router
    ) {}

    ngOnInit() {
        this.pages = this.weeklySurveyService.pages;
        
        this.updatePage();
        this.pageSubscription = this.router.events
        .filter((event) => event instanceof NavigationEnd)
        .subscribe(() => {
            this.updatePage();
        });

        const weekId:string = this.activeRoute.snapshot.paramMap.get('weekId');
        this.weeklySurveyService.loadWeek(weekId);
    }

    updatePage() {
        this.activePage = this.activeRoute.snapshot.firstChild.url[0].path;

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

    prevPage() {
        this.weeklySurveyService.previousPage();
    }

    ngOnDestroy() {
        if(this.pageSubscription) {
            this.pageSubscription.unsubscribe();
        }
    }



}
