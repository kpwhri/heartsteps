import { Component } from "@angular/core";
import { Router } from "@angular/router";
import { FitbitService, FitbitAccount } from "@heartsteps/fitbit/fitbit.service";
import { LoadingService } from "@infrastructure/loading.service";
import moment from "moment";


@Component({
    templateUrl: './fitbit-authorization.page.html'
})
export class FitbitAuthorizationPage {

    public account: FitbitAccount;

    public firstUpdated: Date;
    public lastUpdated: Date;
    public lastDeviceUpdate: Date;

    constructor(
        private router: Router,
        private fitbitService: FitbitService,
        private loadingService: LoadingService
    ) {
        this.fitbitService.account.subscribe((account) => {
            this.account = account;

            this.firstUpdated = account.firstUpdated;
            this.lastDeviceUpdate = account.lastDeviceUpdate;
            if(!moment(account.firstUpdated).isSame(account.lastUpdated)) {
                this.lastUpdated = account.lastUpdated;
            }
        });
        this.refreshData();
    }

    public removeFitbitAccount() {
        this.loadingService.show('Removing Fitbit Account')
        this.fitbitService.removeFitbitAuthorization()
        .catch(() => {})
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public refreshData() {
        this.loadingService.show('Refreshing Fitbit account data')
        this.fitbitService.updateFitbitAccount()
        .catch(() => {})
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public format_date(date: Date): string {
        if (moment(date).isSame(new Date(), 'day')) {
            return moment(date).fromNow();
        } else {
            return moment(date).format('MMMM Do, YYYY');
        }
    }

    public goBack() {
        this.router.navigate([{
            outlets: {
                modal: null
            }
        }]);
    }

}
