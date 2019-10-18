import { Component } from "@angular/core";
import { Router } from "@angular/router";


@Component({
    templateUrl: './fitbit-authorization.page.html'
})
export class FitbitAuthorizationPage {

    constructor(
        private router: Router
    ) {}


    public goBack() {
        this.router.navigate([{
            outlets: {
                modal: null
            }
        }]);
    }

}
