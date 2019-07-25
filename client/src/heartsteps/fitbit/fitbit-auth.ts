import { Component, Output, EventEmitter, OnInit } from '@angular/core';
import { LoadingService } from '@infrastructure/loading.service';
import { FitbitService } from './fitbit.service';
import { AlertDialogController } from '@infrastructure/alert-dialog.controller';

@Component({
    selector: 'heartsteps-fitbit-auth',
    templateUrl: 'fitbit-auth.html'
})
export class FitbitAuth implements OnInit {
    @Output() saved = new EventEmitter<boolean>();

    constructor(
        private loadingService:LoadingService,
        private alertController: AlertDialogController,
        private fitbitService: FitbitService
    ) {}

    ngOnInit() {
        this.fitbitService.isAuthorizing()
        .then(() => {
            this.loadingService.show("Authorizing Fitbit");
            this.fitbitService.updateAuthorization()
            .then(() => {
                this.saved.emit(true)
            })
            .catch(() => {
                this.alertController.show("There was a problem authorizing Fitbit. Please try again.");
            })
            .then(() => {
                this.fitbitService.clearIsAuthorizing();
                this.loadingService.dismiss();
            })
        })
    }

    getAuthorization() {
        this.loadingService.show("Authorizing Fitbit");
        return this.fitbitService.authorize()
        .then(() => {
            setTimeout(() => {
                this.saved.emit(true);
            }, 2000);
        })
        .catch(() => {
            this.alertController.show("There was a problem authorizing Fitbit. Please try again.");
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }
}
