import { Component } from "@angular/core";
import { Router } from "@angular/router";


@Component({
    templateUrl: 'contact-page.html'
})
export class ContactPage {

    constructor(
        private router: Router
    ){}

    goBack() {
        this.router.navigate(['settings']);
    }
}
