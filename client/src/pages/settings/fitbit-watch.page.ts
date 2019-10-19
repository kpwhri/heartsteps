import { Component } from "@angular/core";
import { Router } from "@angular/router";
import { FitbitWatchService } from "@heartsteps/fitbit-watch/fitbit-watch.service";


@Component({
    templateUrl: './fitbit-watch.page.html'
})
export class FitbitWatchPage {

    constructor(
        private router: Router,
        private fitbitWatchService: FitbitWatchService
    ) {}

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
