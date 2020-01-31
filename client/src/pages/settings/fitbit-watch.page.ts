import { Component } from "@angular/core";
import { Router } from "@angular/router";
import { FitbitWatchService } from "@heartsteps/fitbit-watch/fitbit-watch.service";
import moment from "moment";


@Component({
    templateUrl: './fitbit-watch.page.html'
})
export class FitbitWatchPage {

    public installedDate:Date;
    public lastUpdated:Date;

    constructor(
        private router: Router,
        private fitbitWatchService: FitbitWatchService
    ) {
        this.fitbitWatchService.watch.subscribe((watch) => {
            this.installedDate = watch.installed;
            this.lastUpdated = watch.lastUpdated;
        });

        this.fitbitWatchService.udpateStatus()
        .then((watch) => {
            console.log('FitbitWatch', watch)
        });
    }

    public format_date(date: Date) {
        moment(date).format('MMMM Do YYYY')
    }

    public openFitbitPage() {
        this.fitbitWatchService.openWatchInstallPage();
    }

    public goBack() {
        this.router.navigate([{
            outlets: {
                modal: null
            }
        }]);
    }

}
