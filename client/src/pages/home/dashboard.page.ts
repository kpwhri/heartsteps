import { Component } from '@angular/core';
import { WeeklySurveyService, WeeklySurvey } from '@heartsteps/weekly-survey/weekly-survey.service';
import { Router, ActivatedRoute } from '@angular/router';
import { MorningMessageService } from '@heartsteps/morning-message/morning-message.service';
import { MorningMessage } from '@heartsteps/morning-message/morning-message.model';
import { DailySummary } from '@heartsteps/daily-summaries/daily-summary.model';
import { DailySummaryService } from '@heartsteps/daily-summaries/daily-summary.service';
import { CurrentDailySummariesService } from '@heartsteps/current-week/current-daily-summaries.service';

@Component({
    templateUrl: 'dashboard.page.html'
})
export class DashboardPage {

    public morningMessage: MorningMessage;
    public weeklySurvey:WeeklySurvey;
    public today:Date;
    public summary: DailySummary;

    public anchorMessage: string;

    constructor(
        private weeklySurveyService: WeeklySurveyService,
        private morningMessageService: MorningMessageService,
        private dailySummaryService: DailySummaryService,
        private currentDailySummaryService: CurrentDailySummariesService,
        private router: Router,
        private activatedRoute: ActivatedRoute
    ) {
        this.today = new Date();
        this.currentDailySummaryService.today
        .filter(summary => summary !== undefined)
        .subscribe((summary) => {
            this.summary = summary;
        });
        this.dailySummaryService.get(this.today)
        .catch(() => {
            console.log('DashboardPage: Did not update daily summary');
        });

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
