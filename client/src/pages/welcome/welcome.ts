import { Component } from '@angular/core';
import { EnrollmentModal } from '@heartsteps/enrollment/enroll';
import { Router } from '@angular/router';
import { EnrollmentService } from "@heartsteps/enrollment/enrollment.service";

declare var process: {
  env: {
      BUILD_VERSION: string,
      BUILD_DATE: string
  }
}

@Component({
  selector: 'page-welcome',
  templateUrl: 'welcome.html',
  entryComponents: [
    EnrollmentModal
  ]
})
export class WelcomePage {

  public buildVersion: string = process.env.BUILD_VERSION;
  public buildDate: string = process.env.BUILD_DATE;

  constructor(
    private router: Router,
    private enrollmentService: EnrollmentService,
  ) {}

  goToEnrollPage() {
    this.enrollmentService
        .unenroll()
        .catch((error) => {
            console.error("Welcome page, logout:", error);
        })
    this.router.navigate(['enroll']);
  }

}
