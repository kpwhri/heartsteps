import { Component } from "@angular/core";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { EnrollmentService } from "@heartsteps/enrollment/enrollment.service";
import { LoadingService } from "@infrastructure/loading.service";


@Component({
    templateUrl: './enrollment.page.html'
})
export class EnrollmentPage {

    public error: string;
    public form: FormGroup;

    constructor(
        private enrollmentService: EnrollmentService,
        private loadingService: LoadingService
    ) {
        this.form = new FormGroup({
            entryToken: new FormControl('', Validators.required),
            birthYear: new FormControl('', Validators.required)
        });
    }

    public enroll() {
        this.error = undefined;
        this.loadingService.show('Authenticating');

        const token = this.form.value.entryToken;
        const birthYear = this.form.value.birthYear;

        return this.enrollmentService.enroll(token, birthYear)
        .then(() => {
            console.log('Enrolled!!');
        })
        .catch((error) => {
            this.error = error;
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

}
