import { Component, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
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

    public today:Date;
    public formattedDate: string;
    public summary: DailySummary;

    public weeklyGoal: number;

    public anchorMessage: string;

    private resumeSubscription: Subscription;

    constructor(
        private dailySummaryService: DailySummaryService,
        private currentWeekService: CurrentWeekService,
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

        this.dailySummaryService.update(this.today);
        this.resumeSubscription = this.platform.resume.subscribe(() => {
            this.dailySummaryService.update(this.today);
        });

        this.anchorMessage = this.activatedRoute.snapshot.data.anchorMessage;

    }

    ngOnDestroy() {
        if(this.resumeSubscription) {
            this.resumeSubscription.unsubscribe();
        }
    }

}
