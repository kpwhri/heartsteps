import { Component } from "@angular/core";
import { Router } from "@angular/router";


@Component({
    selector: 'enrollment-welcome-page',
    templateUrl: './welcome.page.html'
})
export class WelcomePageComponent {

    constructor(
        private router: Router
    ) {}

    public goToEnrollment() {
        this.router.navigate(['login']);   
    }

}
