import { Component } from "@angular/core";
import { Router } from "@angular/router";

@Component({
    templateUrl: 'generic-messages-modal.html'
})
export class GenericMessagesModal {

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
