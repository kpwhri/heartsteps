import { Component } from "@angular/core";
import { Router } from "@angular/router";
import { FitbitWatchService } from "@heartsteps/fitbit-watch/fitbit-watch.service";
import moment from "moment";
import { LoadingService } from "@infrastructure/loading.service";


@Component({
    templateUrl: './fitbit-watch.page.html'
})
export class FitbitWatchPage {

    public installedDate:Date;
    public lastUpdated:Date;
    public lastChecked:Date;

    constructor(
        private router: Router,
        private fitbitWatchService: FitbitWatchService,
        private loadingService: LoadingService
    ) {
        this.fitbitWatchService.watch.subscribe((watch) => {
            this.installedDate = watch.installed;
            this.lastUpdated = watch.lastUpdated;
            this.lastChecked = watch.lastChecked;
        });
    }

    public format_date(date: Date): string {
        if (moment(date).isSame(new Date(), 'day')) {
            return moment(date).fromNow();
        } else {
            return moment(date).format('MMMM Do, YYYY');
        }
    }

    public openFitbitPage() {
        this.fitbitWatchService.openWatchInstallPage();
    }

    public updateStatus() {
        this.loadingService.show('Checking Clock Face status');
        this.fitbitWatchService.updateStatus()
        .then(()=>{})
        .then(() => {
            this.loadingService.dismiss()
        });
    }

    public goBack() {
        this.router.navigate([{
            outlets: {
                modal: null
            }
        }]);
    }

}
