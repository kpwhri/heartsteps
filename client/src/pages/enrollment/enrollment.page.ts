import { Component } from "@angular/core";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { EnrollmentService } from "@heartsteps/enrollment/enrollment.service";
import { LoadingService } from "@infrastructure/loading.service";
import { Router } from "@angular/router";


@Component({
    templateUrl: './enrollment.page.html'
})
export class EnrollmentPage {

    public error: string;
    public form: FormGroup;

    constructor(
        private enrollmentService: EnrollmentService,
        private loadingService: LoadingService,
        private router: Router
    ) {
        this.form = new FormGroup({
            entryToken: new FormControl('', Validators.required),
            birthYear: new FormControl('', Validators.required)
        });
    }

    public goHome() {
        this.router.navigate(['welcome'])
    }

    public enroll() {
        this.error = undefined;
        const token = this.form.value.entryToken;
        const birthYear = this.form.value.birthYear;

        console.log(`EnrollmentPage enrolling with token ${token} and birth year ${birthYear}`);
        this.loadingService.show('Authenticating');
        return this.enrollmentService.enroll(token, birthYear)
        .then(() => {
            console.log('EnrollmentPage enrollment successful');
            this.loadingService.dismiss();
            console.log('EnrollmentPage navigating to home');
            return this.router.navigate(['/'])
        })
        .catch((error) => {
            console.log('EnrollmentPage enrollment failed', error);
            this.loadingService.dismiss();
            this.error = error;
        });
    }

}
