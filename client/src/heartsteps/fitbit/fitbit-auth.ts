import { Component, Output, EventEmitter } from '@angular/core';
import { loadingService } from '@infrastructure/loading.service';
import { FitbitService } from './fitbit.service';
import { AlertDialogController } from '@infrastructure/alert-dialog.controller';

@Component({
    selector: 'heartsteps-fitbit-auth',
    templateUrl: 'fitbit-auth.html'
})
export class FitbitAuth {
    @Output() saved = new EventEmitter<boolean>();

    constructor(
        private loadingService:loadingService,
        private alertController: AlertDialogController,
        private fitbitService: FitbitService
    ) {}

    getAuthorization() {
        this.loadingService.show("Authorizing Fitbit");
        return this.fitbitService.authorize()
        .then(() => {
            this.saved.emit(true);
        })
        .catch(() => {
            this.alertController.show("There was a problem authorizing Fitbit. Please try again.");
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }
}
