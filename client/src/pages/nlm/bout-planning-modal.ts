import { Component } from "@angular/core";
import { Router } from "@angular/router";

@Component({
    templateUrl: 'bout-planning-modal.html'
})
export class BoutPlanningModal {

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
