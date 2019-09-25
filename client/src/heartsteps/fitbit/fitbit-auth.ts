import { Component, Output, EventEmitter, OnInit } from '@angular/core';
import { LoadingService } from '@infrastructure/loading.service';
import { FitbitService } from './fitbit.service';
import { AlertDialogController } from '@infrastructure/alert-dialog.controller';
import { resolve } from 'path';

@Component({
    selector: 'heartsteps-fitbit-auth',
    templateUrl: 'fitbit-auth.html'
})
export class FitbitAuth implements OnInit {
    @Output() saved = new EventEmitter<boolean>();

    public isAuthorized: boolean;

    constructor(
        private loadingService:LoadingService,
        private alertController: AlertDialogController,
        private fitbitService: FitbitService
    ) {}

    ngOnInit() {
        this.fitbitService.isAuthorizing()
        .then(() => {
            this.updateAuthorization();
        })
        .catch(() => {
            this.update();
        });
    }

    private update(): Promise<void> {
        return this.fitbitService.isAuthorized()
        .then(() => {
            this.isAuthorized = true;
        })
        .catch(() => {
            this.isAuthorized = false;
        })
        .then(() => {
            return undefined;
        })
    }

    private updateAuthorization(): Promise<void> {
        this.loadingService.show("Authorizing Fitbit");
        return this.fitbitService.setIsAuthorizing()
        .then(() => {
            return new Promise((resolve) => {
                setTimeout(resolve, 2000);
            });
        })
        .then(() => {
            return this.fitbitService.updateAuthorization();
        })
        .catch(() => {
            this.showAuthorizationError();
        })
        .then(() => {
            this.fitbitService.clearIsAuthorizing();
            this.loadingService.dismiss();
            return this.update();
        });
    }
    
    private showAuthorizationError(){
        this.alertController.show("There was a problem authorizing Fitbit. Please try again.");
    }

    public nextPage() {
        this.saved.emit(true);
    }

    public authorize() {
        this.loadingService.show("Authorizing Fitbit");
        this.fitbitService.setIsAuthorizing()
        .then(() => {
            return this.fitbitService.authorize();
        })
        .catch(() => {
            this.showAuthorizationError();
        })
        .then(() => {
            this.fitbitService.clearIsAuthorizing();
            this.loadingService.dismiss();
            return this.update();
        });
    }
}
