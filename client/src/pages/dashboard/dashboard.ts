import { Component, ViewChild, ElementRef } from '@angular/core';
import { IonicPage } from 'ionic-angular';
import { ActivityLogService } from '@heartsteps/activity/activity-log.service';
import { DateFactory } from '@infrastructure/date.factory';
import { WeeklySurveyService, WeeklySurvey } from '@heartsteps/weekly-survey/weekly-survey.service';

@IonicPage()
@Component({
    selector: 'page-dashboard',
    templateUrl: 'dashboard.html',
    providers: [
        ActivityLogService,
        DateFactory
    ]
})
export class DashboardPage {

    public weeklySurvey:WeeklySurvey;
    public today:Date;

    constructor(
        private weeklySurveyService: WeeklySurveyService
    ) {
        this.today = new Date();
        this.weeklySurveyService.checkExpiration();
        this.weeklySurveyService.survey.subscribe((survey) => {
            this.weeklySurvey = survey;
        });
    }

    public navigateToWeeklySurvey() {
        this.weeklySurveyService.show();
    }
}
