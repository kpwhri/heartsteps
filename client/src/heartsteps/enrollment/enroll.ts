import { Component, Output, EventEmitter } from '@angular/core';
import { EnrollmentService } from './enrollment.service';
import { LoadingService } from '@infrastructure/loading.service';
import { FormControl, Validators, FormGroup } from '@angular/forms';
import { BrowserService } from '@infrastructure/browser.service';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';


@Component({
    selector: 'heartsteps-enroll',
    templateUrl: 'enroll.html',
    providers: [EnrollmentService]
})
export class EnrollmentModal {
    public error: string
    public enrollmentForm: FormGroup

    @Output('enrolled') enrolled: EventEmitter<boolean> = new EventEmitter();

    constructor(
        private enrollmentService: EnrollmentService,
        private loadingService: LoadingService,
        private browserService: BrowserService,
        private heartstepsServer: HeartstepsServer
    ) {
        console.log("EnrollmentModal.constructor():", this.heartstepsServer);
        this.enrollmentForm = new FormGroup({
            entryToken: new FormControl('', Validators.required),
            birthYear: new FormControl('', Validators.required)
        });
    }

    public enroll() {
        console.log('enrollment/enroll.ts', 'enroll()');
        this.error = undefined;
        this.loadingService.show('Authenticating');

        const token = this.enrollmentForm.value.entryToken;
        const birthYear = this.enrollmentForm.value.birthYear;
        console.log('src', 'enrollment/enroll.ts', 'enroll()', 'token', token, 'birthYear', birthYear);
        this.enrollmentService.enroll(token, birthYear)
            .then(() => {
                console.log('enrollment/enroll.ts', 'enroll()', 'enrollment successful');
                this.enrolled.emit(true);
            })
            .catch((error) => {
                console.log('enrollment/enroll.ts', 'enroll()', 'enrollment failed', error);
                console.log(error);
                this.error = error;
            })
            .then(() => {
                console.log('enrollment/enroll.ts', 'enroll()', 'enrollment complete');
                this.loadingService.dismiss();
            });
    }

    public openPrivacyPolicy() {
        const url = this.heartstepsServer.makeUrl('privacy-policy');
        this.browserService.open(url);
    }
}
