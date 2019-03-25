import { Component } from "@angular/core";
import { Router } from "@angular/router";


@Component({
    templateUrl: './enroll.page.html'
})
export class EnrollPageComponent {
    
    constructor(
        private router: Router
    ) {}

    public dismiss() {
        return this.router.navigate([{outlets:{
            modal: null
        }}]);
    }

    public continue() {
        this.router.navigate(['onboard'])
        .then(() => {
            this.dismiss();
        });
    }

}
