import { Component, Output, EventEmitter } from '@angular/core';
import { LoadingService } from '@infrastructure/loading.service';
import { FitbitService } from '@heartsteps/fitbit/fitbit.service';
import { AlertDialogController } from '@infrastructure/alert-dialog.controller';
import { BrowserService } from '@infrastructure/browser.service';

@Component({
    selector: 'heartsteps-fitbit-auth',
    templateUrl: 'fitbit-auth.page.html'
})
export class FitbitAuthPage {
    @Output() saved = new EventEmitter<boolean>();

    constructor(
        public loadingService:LoadingService,
        public alertController: AlertDialogController,
        public fitbitService: FitbitService,
        public browserService: BrowserService
    ) {}

    private showAuthorizationError(){
        this.alertController.show("There was a problem authorizing Fitbit. Please try again.");
    }

    public nextPage() {
        this.saved.emit(true);
    }

    public update() {
        this.loadingService.show('Updating fitbit authorization');
        this.fitbitService.updateFitbitAccount()
        .then(() => {
            return this.fitbitService.isAuthorized();
        })
        .then(() => {
            this.nextPage();
        })
        .catch(() => {
            this.alertController.show('Your fitbit account is unauthorized. Connect to Fitbit to continue.');
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public authorize() {
        this.loadingService.show("Authorizing Fitbit");
        // this.fitbitService.setRedirectURL('/api/fitbit/authorize/process');
        return this.fitbitService.startAuthorization()
        .catch(() => {
            this.showAuthorizationError();
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }
}
