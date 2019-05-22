import { Component, OnDestroy } from '@angular/core';
import { WeeklySurveyService, WeeklySurvey } from '@heartsteps/weekly-survey/weekly-survey.service';
import { Router, ActivatedRoute } from '@angular/router';
import { MorningMessageService } from '@heartsteps/morning-message/morning-message.service';
import { MorningMessage } from '@heartsteps/morning-message/morning-message.model';
import { DailySummary } from '@heartsteps/daily-summaries/daily-summary.model';
import { DailySummaryService } from '@heartsteps/daily-summaries/daily-summary.service';
import * as moment from 'moment';
import { Platform } from 'ionic-angular';
import { Subscription } from 'rxjs';
import { CurrentWeekService } from '@heartsteps/current-week/current-week.service';

@Component({
    templateUrl: 'dashboard.page.html'
})
export class DashboardPage implements OnDestroy {

    public morningMessage: MorningMessage;
    public weeklySurvey:WeeklySurvey;
    public today:Date;
    public formattedDate: string;
    public summary: DailySummary;

    public weeklyGoal: number;

    public anchorMessage: string;

    private resumeSubscription: Subscription;

    constructor(
        private weeklySurveyService: WeeklySurveyService,
        private morningMessageService: MorningMessageService,
        private dailySummaryService: DailySummaryService,
        private currentWeekService: CurrentWeekService,
        private router: Router,
        private activatedRoute: ActivatedRoute,
        private platform: Platform
    ) {
        this.today = new Date();
        this.formattedDate = moment().format("dddd, M/D");

        this.dailySummaryService.watch(this.today)
        .subscribe((summary) => {
            this.summary = summary;
        });

        this.currentWeekService.week
        .filter(week => week !== undefined)
        .subscribe((week) => {
            this.weeklyGoal = week.goal;
        });

        this.dailySummaryService.get(this.today);
        this.resumeSubscription = this.platform.resume.subscribe(() => {
            this.dailySummaryService.get(this.today);
        });

        this.anchorMessage = this.activatedRoute.snapshot.data.anchorMessage;

        this.weeklySurveyService.checkExpiration();
        this.weeklySurveyService.survey.subscribe((survey) => {
            this.weeklySurvey = survey;
        });

        this.morningMessageService.get()
        .then((morningMessage) => {
            if(!morningMessage.surveyComplete) {
                this.morningMessage = morningMessage;
            }
        })
        .catch(() => {
            console.log('No morning message');
        });
    }

    ngOnDestroy() {
        if(this.resumeSubscription) {
            this.resumeSubscription.unsubscribe();
        }
    }

    public navigateToWeeklySurvey() {
        this.router.navigate(['weekly-survey']);
    }

    public navigateToMorningMessage() {
        this.router.navigate(['morning-survey']);
    }
}
