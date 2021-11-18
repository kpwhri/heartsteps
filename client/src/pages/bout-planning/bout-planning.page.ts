import { Component, OnInit } from "@angular/core";
import { Router } from "@angular/router";
// import { WeeklySurveyService as HeartstepsWeeklySurveyService } from "@heartsteps/weekly-survey/weekly-survey.service";
// import { SurveyStartPage } from "./survey-start.page";
// import { SurveyComponent } from "./survey.component";
// import { NextWeekGoalComponent } from "./next-week-goal.component";
// import { NextWeekPlansComponent } from "./next-week-plans.component";
// import { BarriersComponent } from "./barriers.component";

@Component({
    templateUrl: './bout-planning.page.html'
})
export class BoutPlanningPage implements OnInit {

    public pages:Array<any>;

    constructor(
        // private weeklySurveyService: HeartstepsWeeklySurveyService,
        private router: Router
    ) {}

    ngOnInit() {
        // this.pages = [{
        //     key: 'start',
        //     title: 'Weekly Review',
        //     component: SurveyStartPage
        // }, {
        //     key: 'survey',
        //     title: 'Weekly Questions',
        //     component: SurveyComponent
        // },
        // {
        //     key: 'barriers',
        //     title: 'Weekly Barriers',
        //     component: BarriersComponent
        // }, {
        //     key:'next-goal',
        //     title: 'Next Goal',
        //     component: NextWeekGoalComponent
        // }, {
        //     key:'next-plans',
        //     title: 'Next Week',
        //     component: NextWeekPlansComponent
        // }];
    }

    finish() {
        // this.weeklySurveyService.complete();
        this.router.navigate(['/']);
    }
}
