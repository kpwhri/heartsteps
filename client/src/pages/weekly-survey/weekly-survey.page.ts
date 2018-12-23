import { Component, OnInit, OnDestroy } from "@angular/core";
import { Router, ActivatedRoute, ParamMap, UrlSegment } from "@angular/router";
import { Subscription } from "rxjs";
import { WeeklySurveyService } from "./weekly-survey.service";

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
        private activeRoute: ActivatedRoute
    ) {}

    ngOnInit() {
        const weekId:string = this.activeRoute.snapshot.paramMap.get('weekId');
        this.weeklySurveyService.loadWeek(weekId)
        .then(() => {
            this.pages = this.weeklySurveyService.pages;
            this.pageSubscription = this.weeklySurveyService.currentPage.subscribe((page:string) => {
                this.activePage = page;
                this.setPageTitle(page);
                if(this.pages.indexOf(this.activePage) === 0) {
                    this.firstPage = true;
                } else {
                    this.firstPage = false;
                }
            });
        })
    }

    setPageTitle(page:string) {
        if (page == 'survey') {
            this.title = "Weekly Questions";
        } else if (page == 'goal') {
            this.title = "New goal for upcoming week"
        } else {
            this.title = "Weekly Review";
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
