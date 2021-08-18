import { Component } from '@angular/core';
import { DailySummaryService } from '@heartsteps/daily-summaries/daily-summary.service';
import { LoadingService } from '@infrastructure/loading.service';
import moment from 'moment';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';
import { Router } from '@angular/router';

class Log {
    public timestamp: string;
    public status: string;
    public action: string;
}

@Component({
    templateUrl: 'user-logs.page.html',
    selector: 'user-logs-page'
})
export class UserLogsPage {
        public serializeduserlogs: Array;
    constructor(
        private heartstepsServer: HeartstepsServer,
        private router: Router
    ) {
        this.update();
    }

    private update() {
        this.serializeduserlogs = []
        this.heartstepsServer.get('userlogs')
        .then((data) => {
            console.log(data);
            console.log('GET LATEST USER LOGS: Got a response from the server');

            var temparray = [];

            for (let i = 0; i < data.logs.length; i++) {

//                 console.log(data.logs[i].action);
//                 console.log(data.logs[i].timestamp);
//                 console.log(data.logs[i].status);
//
//                 serializeduserlogs[i].action = data.logs[i].action;
//                 serializeduserlogs[i].timestamp = data.logs[i].timestamp;
//                 serializeduserlogs[i].status = data.logs[i].status;

                var temp = {timestamp: data.logs[i].timestamp, status: data.logs[i].status, action: data.logs[i].action};
//                 serializeduserlogs.push(temp);
                temparray.push(temp);
            }
            console.log(temparray);
            this.serializeduserlogs = temparray.slice();
            console.log(this.serializeduserlogs);
        })
        .catch(() => {
            console.log('User logs failed')
        })
    }

//     private getArray() {
//         var array = [1,2,3];  // As an example
//
//         var ans = "<TABLE><TR>";
//         for(i=0; i<array.length; i++) {
//             ans += "<TD>" + array[i] + "</TD>";
//         }
//         ans += "</TR></TABLE>"
//
//         document.write(ans);
//     }

//     private dateToDay(date: Date): Day {
//         day.date = date;
//         day.isToday = moment().isSame(moment(day.date), 'day');
//         return day;
//     }

//     public format_short_date(date: Date): string {
//         return moment(date).format('MM/DD');
//     }
//
//     public format_date(date: Date): string {
//         return moment(date).format("dddd, M/D");
//     }
//
//     public format_time_ago(date: Date): string {
//         return moment(date).fromNow();
//     }

    public goToSettings() {
        this.router.navigate(['settings']);
    }

}
