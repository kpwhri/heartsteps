import { Component } from "@angular/core";
import { Router } from "@angular/router";

@Component({
    templateUrl: 'blank-page.html'
})
export class BlankPage {

    constructor(
        private router: Router
    ){}

    goBack() {
        this.router.navigate([{
            outlets: {
                modal: null
            }
        }]);
    }
}
