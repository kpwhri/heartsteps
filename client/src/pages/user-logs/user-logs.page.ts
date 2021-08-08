import { Component } from '@angular/core';
import { DailySummaryService } from '@heartsteps/daily-summaries/daily-summary.service';
import { LoadingService } from '@infrastructure/loading.service';
import moment from 'moment';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';

class Log {
    public date: Date;
    public message: string;
    public type: string;
}

@Component({
    templateUrl: 'user-logs.page.html',
    selector: 'user-logs-page'
})
export class UserLogsPage {

    public logs: Array<Log>;

    constructor(
        private heartstepsServer: HeartstepsServer
    ) {
        this.update()
    }

    private update() {
        this.heartstepsServer.get('userlogs')
        .then((data) => {
            console.log(data);
            console.log('GET LATEST GOAL: Got a response from the server');

            this.dailyStepGoal = data;
        })
        .catch(() => {
            console.log('User logs failed')
        })
    }

    private dateToDay(date: Date): Day {
        day.date = date;
        day.isToday = moment().isSame(moment(day.date), 'day');
        return day;
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
