import { Component, Output, EventEmitter, OnInit, OnDestroy } from '@angular/core';
import { LoadingService } from '@infrastructure/loading.service';
import { FitbitService } from '@heartsteps/fitbit/fitbit.service';
import { AlertDialogController } from '@infrastructure/alert-dialog.controller';
import { BrowserService } from '@infrastructure/browser.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'heartsteps-fitbit-auth',
    templateUrl: 'fitbit-auth.page.html'
})
export class FitbitAuthPage implements OnInit, OnDestroy {
    @Output() saved = new EventEmitter<boolean>();

    private closedSubscription: Subscription;

    constructor(
        public loadingService:LoadingService,
        public alertController: AlertDialogController,
        public fitbitService: FitbitService,
        public browserService: BrowserService
    ) {}
    
    public ngOnInit() {
        this.closedSubscription = this.browserService.closed.subscribe(() => {
            this.update();
        });
    }

    public ngOnDestroy() {
        this.closedSubscription.unsubscribe();
    }

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
        return this.fitbitService.startAuthorization()
        .catch(() => {
            this.showAuthorizationError();
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }
}
