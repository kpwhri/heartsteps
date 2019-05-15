import { Component } from "@angular/core";
import { Router } from "@angular/router";


@Component({
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
