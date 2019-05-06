import { Component, OnInit } from "@angular/core";
import { Router, ActivatedRoute } from "@angular/router";
import { WeeklySurveyService as HeartstepsWeeklySurveyService, WeeklySurvey } from "@heartsteps/weekly-survey/weekly-survey.service";
import { SurveyStartPage } from "./survey-start.page";
import { SurveyComponent } from "./survey.component";
import { NextWeekGoalComponent } from "./next-week-goal.component";
import { NextWeekPlansComponent } from "./next-week-plans.component";

@Component({
    templateUrl: './weekly-survey.page.html'
})
export class WeeklySurveyPage implements OnInit {

    public pages:Array<any>;
    private weeklySurvey: WeeklySurvey;

    constructor(
        private weeklySurveyService: HeartstepsWeeklySurveyService,
        private activatedRoute: ActivatedRoute,
        private router: Router
    ) {}

    ngOnInit() {
        this.weeklySurvey = this.activatedRoute.snapshot.data['weeklySurvey'];
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
            title: 'Next Goal',
            component: NextWeekGoalComponent
        }, {
            key:'next-plans',
            title: 'Next Week',
            component: NextWeekPlansComponent
        }];
    }

    finish() {
        this.weeklySurveyService.complete();
        this.router.navigate(['/']);
    }
}
