import { Component, Output, EventEmitter, OnInit } from "@angular/core";
import { Router } from "@angular/router";
import { LoadingService } from "@infrastructure/loading.service";
import { FitbitService } from "@heartsteps/fitbit/fitbit.service";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";


@Component({
    templateUrl: 'fitbit-authorize.page.html'
})
export class FitbitAuthorizePage implements OnInit{


    @Output() saved = new EventEmitter<boolean>();

    constructor(
        private router: Router,
        private loadingService:LoadingService,
        private alertController: AlertDialogController,
        private fitbitService: FitbitService
    ) {}

    ngOnInit() {
        this.loadingService.show('Updating Fitbit Authorization');
        this.fitbitService.updateAuthorization()
        .then(() => {
            return this.fitbitService.isAuthorized()
            .then(() => {
                return this.router.navigate(['setup', 'complete'])
            })
        })
        .catch(() => {
            this.router.navigate(['setup', 'fitbit'])
        })
        .then(() => {
            this.loadingService.dismiss();
        });
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
