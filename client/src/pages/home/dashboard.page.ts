import { Component } from '@angular/core';
import { WeeklySurveyService, WeeklySurvey } from '@heartsteps/weekly-survey/weekly-survey.service';
import { Router, ActivatedRoute } from '@angular/router';
import { MorningMessageService } from '@heartsteps/morning-message/morning-message.service';
import { MorningMessage } from '@heartsteps/morning-message/morning-message.model';
import { DailySummary } from '@heartsteps/daily-summaries/daily-summary.model';
import { DailySummaryService } from '@heartsteps/daily-summaries/daily-summary.service';
import * as moment from 'moment';

@Component({
    templateUrl: 'dashboard.page.html'
})
export class DashboardPage {

    public morningMessage: MorningMessage;
    public weeklySurvey:WeeklySurvey;
    public today:Date;
    public formattedDate: string;
    public summary: DailySummary;

    public anchorMessage: string;

    constructor(
        private weeklySurveyService: WeeklySurveyService,
        private morningMessageService: MorningMessageService,
        private dailySummaryService: DailySummaryService,
        private router: Router,
        private activatedRoute: ActivatedRoute
    ) {
        this.today = new Date();
        this.formattedDate = moment().format("dddd, M/D");

        this.dailySummaryService.watch(this.today)
        .subscribe((summary) => {
            this.summary = summary;
        });
        this.dailySummaryService.get(this.today);

        this.anchorMessage = this.activatedRoute.snapshot.data.anchorMessage;

        this.weeklySurveyService.checkExpiration();
        this.weeklySurveyService.survey.subscribe((survey) => {
            this.weeklySurvey = survey;
        });

        this.morningMessageService.get()
        .then((morningMessage) => {
            this.morningMessage = morningMessage;
        })
        .catch(() => {
            console.log('No morning message');
        });
    }

    public navigateToWeeklySurvey() {
        this.router.navigate(['weekly-survey']);
    }

    public navigateToMorningMessage() {
        this.router.navigate(['morning-survey']);
    }
}
