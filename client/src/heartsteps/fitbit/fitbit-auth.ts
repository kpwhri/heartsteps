import { Component, Output, EventEmitter } from '@angular/core';
import { loadingService } from '@infrastructure/loading.service';
import { FitbitService } from './fitbit.service';

@Component({
    selector: 'heartsteps-fitbit-auth',
    templateUrl: 'fitbit-auth.html'
})
export class FitbitAuth {
    @Output() saved = new EventEmitter<boolean>();

    constructor(
        private loadingService:loadingService,
        private fitbitService: FitbitService
    ) {}

    getAuthorization() {
        this.loadingService.show("Authorizing Fitbit");
        return this.fitbitService.authorize()
        .then(() => {
            this.saved.emit(true);
        })
        .catch(() => {
            console.log("Authorization failed")
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }
}
