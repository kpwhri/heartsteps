import { Component } from "@angular/core";
import { Router } from "@angular/router";


@Component({
    templateUrl: 'reflection-time-page.html'
})
export class ReflectionTimePage {

    constructor(
        private router: Router
    ){}

    goBack() {
        this.router.navigate(['settings']);
    }
}
