import { Component } from "@angular/core";
import { Router } from "@angular/router";


@Component({
    templateUrl: 'suggestion-times.html'
})
export class SuggestionTimesPage {

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