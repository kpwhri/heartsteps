import { Component } from '@angular/core';
import { DailySummaryService } from '@heartsteps/daily-summaries/daily-summary.service';
import { LoadingService } from '@infrastructure/loading.service';
import moment from 'moment';
import { DailySummary } from '@heartsteps/daily-summaries/daily-summary.model';
import { Router } from '@angular/router';
import { ParticipantInformationService } from '@heartsteps/participants/participant-information.service';
// import { promises } from 'fs';
import { ParticipantService } from '@heartsteps/participants/participant.service';

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
    public baselinePeriod: Number;

    public studyContactName: string;
    public studyContactPhone: string;

    constructor(
        private loadingService: LoadingService,
        private router: Router,
        private dailySummaryService: DailySummaryService,
        private participantService: ParticipantService,
        private participantInformationService: ParticipantInformationService,
    ) {
        this.dailySummaryService.setup();
        this.dailySummaryService.watch(new Date())
        .subscribe((summary) => {
            this.summary = summary;
        });
        this.participantInformationService.getStudyContactInformation()
        .then((contactInformation) => {
            this.studyContactName = contactInformation.name;
            this.studyContactPhone = contactInformation.number;
        })
        this.reload();
    }

    public reload() {
        console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "reload()", 1);
        
        console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "reload()", 2);

        this.participantService.update()
        .then(() => {
            return this.participantInformationService.load();
        }).then(() => {
            this.loadingService.show('Checking if the baseline is complete');
            return this.participantInformationService.getBaselineComplete();
        }).then((baselineComplete) => {
            this.loadingService.dismiss();
            console.log("[baseline-week.page.ts-BaselineWeekPage] baselineComplete", baselineComplete);
            if (baselineComplete) {
                this.router.navigate(['/']);
            } else {
                var autoUpdate = undefined;
                autoUpdate = setTimeout(() => {
                    this.reload();
                }, 5000);
            }
            this.loadingService.show('Loading activity data');
            return this.dailySummaryService.reload();
        }).then(() => {
            this.loadingService.dismiss();
            return this.setDays();
        }).catch((err) => {
            console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "reload()", 5);
            console.error(err);
        })

        // this.participantService.update()
        // .then(() => {
        //     console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "reload()", 3);
        //     this.participantInformationService.load()
        //     .then(() => {
        //         this.participantInformationService.getBaselineComplete()
        //         .then((baselineComplete) => {
        //             console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "reload()", 3, "baselineComplete", baselineComplete);
        //             if(baselineComplete) {
        //                 this.router.navigate(['/']);
        //             } else {
        //                 var autoUpdate = undefined;
        //                 autoUpdate = setTimeout(() => {
        //                     this.reload();
        //                 }, 5000);
        //             }
        //         });
        //     });            
        //     return this.dailySummaryService.reload();
        // })
        // .then(() => {
        //     console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "reload()", 4);
        //     this.participantInformationService.getBaselineComplete()
        //     .then((baselineComplete) => {
        //         if(baselineComplete) {
        //             this.router.navigate(['/']);
        //         }
        //     });
        //     return this.setDays();
        // })
        // .catch((err) => {
        //     console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "reload()", 5);
        //     console.error(err);
        // })
        // .then(() => {
        //     console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "reload()", 6);
        //     return this.participantInformationService.getBaselineComplete()
        // })
        // .then((isBaselineComplete) => {
        //     console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "reload()", 7);
        //     this.loadingService.dismiss();
        //     console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "reload()", 8);
        //     console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "reload(): isBaselineComplete", isBaselineComplete);
        //     if (isBaselineComplete) {
        //         console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "reload()", 9);
        //         this.router.navigate(['/']);
        //     }
        // });
    }

    private dateToDay(date: Date, woreFitbit: boolean): Day {
        const day = new Day();
        day.date = date;
        day.isToday = moment().isSame(moment(day.date), 'day');
        day.woreFitbit = woreFitbit;
        return day;
    }

    private setBaselinePeriod(): Promise<void> {
        return this.participantInformationService.getBaselinePeriod()
        .then((baselinePeriod) => {
            this.baselinePeriod = baselinePeriod;
            return undefined
        })
        .catch(() => {
            this.baselinePeriod = 7;
            return Promise.resolve(undefined);
        })
    }

    private setDays(): Promise<void> {
        console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", 1);
        return this.setBaselinePeriod()
        .then(() => {
            console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", 2);
            return this.dailySummaryService.getAll()
        })
        .then((dailySummaries) => {
            console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", 3);
            console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", "dailySummaries", dailySummaries);
            const days: Array<Day> = [];
            dailySummaries.forEach((summary) => {
                console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", 4);
                console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", "summary.date", summary.date);
                console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", "summary.wore_fitbit", summary.wore_fitbit);
                const day = this.dateToDay(summary.date, summary.wore_fitbit);
                console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", "day.date", day.date);
                console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", "day.isToday", day.isToday);
                console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", "day.woreFitbit", day.woreFitbit);
                console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", 5);
                if(day.woreFitbit) {
                    days.push(day);
                }
            });
            console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", "days", days);
            console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", 6);
            this.numberDaysWorn = days.length;
            console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", 7);
            let date = new Date();
            if(days.length) {
                console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", 8);
                date = days[days.length-1].date;
            }
            
            while(days.length <= this.baselinePeriod) {
                console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", 9);
                date = moment(date).add(1, 'days').toDate();
                console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", 10);
                const day = this.dateToDay(date, false);
                console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", 11);
                days.push(day);
            }
            console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", 12);
            this.days = days;
        })
        .catch((error) => {
            console.log("src", "pages", "baseline-week", "baseline-week.page.ts", "BaseLineWeekPage", "setDays()", 13);
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
