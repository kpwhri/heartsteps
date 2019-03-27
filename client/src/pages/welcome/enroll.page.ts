import { Component } from "@angular/core";
import { Router } from "@angular/router";


@Component({
    templateUrl: './enroll.page.html'
})
export class EnrollPageComponent {
    
    constructor(
        private router: Router
    ) {}

    public dismiss(): Promise<boolean> {
        return this.router.navigate([{outlets:{
            modal: null
        }}])
        .then(() => {
            return true;
        });
    }

    public continue() {
        this.dismiss()
        .then(() => {
            this.router.navigate(['onboard']);
        })
    }

}
