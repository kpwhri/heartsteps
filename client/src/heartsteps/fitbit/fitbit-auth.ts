import { Component, Output, EventEmitter, OnInit } from '@angular/core';
import { LoadingService } from '@infrastructure/loading.service';
import { FitbitService } from './fitbit.service';
import { AlertDialogController } from '@infrastructure/alert-dialog.controller';
// import { resolve } from 'path';

@Component({
    selector: 'heartsteps-fitbit-auth',
    templateUrl: 'fitbit-auth.html'
})
export class FitbitAuth {
    @Output() saved = new EventEmitter<boolean>();

    constructor(
        public loadingService:LoadingService,
        public alertController: AlertDialogController,
        public fitbitService: FitbitService
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
            this.alertController.show('Unauthroized');
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public authorize() {
        this.loadingService.show("Authorizing Fitbit");
        return this.fitbitService.authorize()
        .then(() => {
            this.nextPage();            
        })
        .catch(() => {
            this.showAuthorizationError();
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }
}
