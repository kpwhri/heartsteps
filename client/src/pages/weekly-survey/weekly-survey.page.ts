import { Component, OnInit } from "@angular/core";
import { Router, ActivatedRoute } from "@angular/router";
import { WeeklySurveyService as HeartstepsWeeklySurveyService } from "@heartsteps/weekly-survey/weekly-survey.service";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { SurveyStartPage } from "./survey-start.page";
import { SurveyComponent } from "./survey.component";
import { NextWeekGoalComponent } from "./next-week-goal.component";
import { NextWeekPlansComponent } from "./next-week-plans.component";

@Component({
    templateUrl: './weekly-survey.page.html'
})
export class WeeklySurveyPage implements OnInit {

    pages:Array<any>;
    week:Week;

    constructor(
        private weeklySurvey: HeartstepsWeeklySurveyService,
        private activatedRoute: ActivatedRoute,
        private router: Router
    ) {}

    ngOnInit() {
        this.week = this.activatedRoute.snapshot.data['weeks'][0];
        this.pages = [{
            key: 'start',
            title: 'Weekly Review',
            component: SurveyStartPage
        }, {
            key: 'survey',
            title: 'Weekly Questions',
            component: SurveyComponent
        }, {
            key:'next-goal',
            title: 'New goal for upcoming week',
            component: NextWeekGoalComponent
        }, {
            key:'next-plans',
            title: 'Make plans for next week',
            component: NextWeekPlansComponent
        }];
    }

    finish() {
        this.weeklySurvey.complete();
        this.router.navigate(['/']);
    }
}
