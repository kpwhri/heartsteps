import { Component } from "@angular/core";
import { Router } from "@angular/router";


@Component({
    templateUrl: 'places-page.html'
})
export class PlacesPage {

    constructor(
        private router: Router
    ){}

    goBack() {
        this.router.navigate(['settings']);
    }
}
