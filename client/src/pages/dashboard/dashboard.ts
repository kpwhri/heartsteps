import { Component, OnInit } from '@angular/core';
import { IonicPage } from 'ionic-angular';
import { ActivityLogService } from '@heartsteps/activity-logs/activity-log.service';
import { DateFactory } from '@infrastructure/date.factory';
import { WeeklySurveyService, WeeklySurvey } from '@heartsteps/weekly-survey/weekly-survey.service';
import { DailySummaryService } from '@heartsteps/daily-summaries/daily-summary.service';
import { Router } from '@angular/router';

@IonicPage()
@Component({
    selector: 'page-dashboard',
    templateUrl: 'dashboard.html',
    providers: [
        ActivityLogService,
        DateFactory
    ]
})
export class DashboardPage implements OnInit {

    public weeklySurvey:WeeklySurvey;
    public today:Date;

    constructor(
        private weeklySurveyService: WeeklySurveyService,
        private dailySummaryService: DailySummaryService,
        private router: Router
    ) {
        this.today = new Date();
        this.weeklySurveyService.checkExpiration();
        this.weeklySurveyService.survey.subscribe((survey) => {
            this.weeklySurvey = survey;
        });
    }

    ngOnInit() {
        this.dailySummaryService.update(new Date());
    }

    public navigateToWeeklySurvey() {
        this.router.navigate(['weekly-survey']);
    }
}
