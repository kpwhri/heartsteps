import { Component } from '@angular/core';
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
    public serializeduserlogs: Array<Log>;
    public numLogs: number;
    constructor(
        private heartstepsServer: HeartstepsServer,
        private router: Router
    ) {
        this.update();
    }

    private update() {
        this.serializeduserlogs = [];
        this.heartstepsServer.get('userlogs')
        .then((data) => {
            console.log(data);
            console.log('GET LATEST USER LOGS: Got a response from the server');

            var temparray = [];

            for (let i = 0; i < data.logs.length; i++) {
                var temp = { timestamp: data.logs[i].timestamp, status: data.logs[i].status, action: data.logs[i].action };
                temparray.push(temp);
            }

            console.log(temparray);
            this.serializeduserlogs = temparray.slice();
            console.log(this.serializeduserlogs);
            this.numLogs = data.logs.length;
        })
            .catch(() => {
                console.log('User logs failed')
            })
    }

    public dismiss() {
        this.router.navigate(['home', 'settings']);
    }

}
