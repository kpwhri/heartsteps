import { Component } from '@angular/core';
import { DailySummaryService } from '@heartsteps/daily-summaries/daily-summary.service';
import { LoadingService } from '@infrastructure/loading.service';
import moment from 'moment';
import { DailySummary } from '@heartsteps/daily-summaries/daily-summary.model';
import { Router } from '@angular/router';
import { ParticipantInformationService } from '@heartsteps/participants/participant-information.service';

class Day {
    public date: Date;
    public woreFitbit: boolean;
    public isToday: boolean;
}

@Component({
    templateUrl: 'baseline-week.page.html',
    selector: 'baseline-week-page'
})
export class BaselineWeekPage {

    public summary: DailySummary;

    public days: Array<Day>;
    public numberDaysWorn: Number;

    public studyContactName: string = 'Grace Do';
    public studyContactPhone: string = '(310) 555-5555';

    constructor(
        private loadingService: LoadingService,
        private router: Router,
        private dailySummaryService: DailySummaryService,
        private participantInformationService: ParticipantInformationService
    ) {
        this.dailySummaryService.watch(new Date())
        .subscribe((summary) => {
            this.summary = summary;
        });
        this.reload();
    }

    public reload() {
        this.loadingService.show('Loading activity data');
        this.dailySummaryService.reload()
        .then(() => {
            return this.setDays();
        })
        .catch((err) => {
            console.error(err);
        })
        .then(() => {
            this.loadingService.dismiss();
        })
    }

    private dateToDay(date: Date, woreFitbit: boolean): Day {
        const day = new Day();
        day.date = date;
        day.isToday = moment().isSame(moment(day.date), 'day');
        day.woreFitbit = woreFitbit;
        return day;
    }

    private setDays(): Promise<void> {
        return this.dailySummaryService.getAll()
        .then((dailySummaries) => {
            const days: Array<Day> = [];
            dailySummaries.forEach((summary) => {
                const day = this.dateToDay(summary.date, summary.wore_fitbit);
                if(day.woreFitbit) {
                    days.push(day);
                }
            });
            this.numberDaysWorn = days.length;
    
            let date = new Date();
            if(days.length) {
                date = days[days.length-1].date;
            }
            while(days.length <= 7) {
                date = moment(date).add(1, 'days').toDate();
                const day = this.dateToDay(date, false);
                days.push(day);
            }
            this.days = days;

        })
        .catch((error) => {
            console.log('errors', error)
        });
    }

    public format_short_date(date: Date): string {
        return moment(date).format('MM/DD');
    }

    public format_date(date: Date): string {
        return moment(date).format("dddd, M/D");
    }

    public format_time_ago(date: Date): string {
        return moment(date).fromNow();
    }

    public goToSettings() {
        this.router.navigate(['settings']);
    }

}
