import { Component, Output, EventEmitter } from "@angular/core";
import { FitbitWatchService } from "./fitbit-watch.service";
import { LoadingService } from "@infrastructure/loading.service";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";

@Component({
    selector: 'heartsteps-watch-setup',
    templateUrl: './watch-setup.component.html'
})
export class WatchSetupComponent {

    @Output('saved') saved: EventEmitter<boolean> = new EventEmitter();

    constructor(
        private fitbitWatchService: FitbitWatchService,
        private loadingService: LoadingService,
        private alertDialogController: AlertDialogController
    ) {}

    public openFitbitPage() {
        this.fitbitWatchService.openWatchInstallPage();
    }

    public checkComplete() {
        this.loadingService.show('Checking HeartSteps Clock Face status')
        this.fitbitWatchService.updateStatus()
        .then((fitbitWatch) => {
            this.loadingService.dismiss();
            if (fitbitWatch.isInstalled()) {
                this.saved.emit(true);
            } else {
                this.loadingService.dismiss();
                this.alertDialogController.show('Fitbit watch not installed');
            }
        })
    }

    public skip() {
        this.saved.emit(true);
    }

}
