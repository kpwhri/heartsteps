import { Component, OnInit } from "@angular/core";
import { Router } from "@angular/router";
import { LoadingService } from "@infrastructure/loading.service";
import { FitbitService } from "@heartsteps/fitbit/fitbit.service";
import { FitbitAuth } from "@heartsteps/fitbit/fitbit-auth";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";


@Component({
    template: ''
})
export class FitbitAuthorizePage extends FitbitAuth implements OnInit{

    constructor(
        alertDialogController: AlertDialogController,
        fitbitService: FitbitService,
        loadingService: LoadingService,
        private router: Router
    ) {
        super(loadingService, alertDialogController, fitbitService);
    }

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

}
