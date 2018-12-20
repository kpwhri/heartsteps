import { Component } from "@angular/core";
import { Location } from "@angular/common";


@Component({
    templateUrl: 'places-page.html'
})
export class PlacesPage {

    constructor(
        private location:Location
    ){}

    goBack() {
        this.location.back();
    }
}
