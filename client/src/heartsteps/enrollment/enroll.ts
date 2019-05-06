import { Component, Output, EventEmitter } from '@angular/core';
import { EnrollmentService } from './enrollment.service';
import { LoadingService } from '@infrastructure/loading.service';
import { FormControl, Validators, FormGroup } from '@angular/forms';
import { BrowserService } from '@infrastructure/browser.service';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';


@Component({
    selector: 'heartsteps-enroll',
    templateUrl: 'enroll.html',
    providers: [ EnrollmentService ]
})
export class EnrollmentModal {
    public error:string
    public enrollmentForm:FormGroup

    @Output('enrolled') enrolled:EventEmitter<boolean> = new EventEmitter();

    constructor(
        private enrollmentService: EnrollmentService,
        private loadingService:LoadingService,
        private browserService: BrowserService,
        private heartstepsServer: HeartstepsServer
    ) {
        this.enrollmentForm = new FormGroup({
            entryToken: new FormControl('', Validators.required),
            birthYear: new FormControl('', Validators.required)
        });
    }

    public enroll() {
        this.error = undefined;
        this.loadingService.show('Authenticating');

        const token = this.enrollmentForm.value.entryToken;
        const birthYear = this.enrollmentForm.value.birthYear;
        
        this.enrollmentService.enroll(token, birthYear)
        .then(() => {
            this.enrolled.emit(true);
        })
        .catch((error) => {
            this.error = error;
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public openPrivacyPolicy() {
        const url = this.heartstepsServer.makeUrl('privacy-policy');
        this.browserService.open(url);
    }
}
