import { Component } from "@angular/core";
import { Location } from "@angular/common";


@Component({
    templateUrl: 'contact-page.html'
})
export class ContactPage {

    constructor(
        private location:Location
    ){}

    goBack() {
        this.location.back();
    }
}
