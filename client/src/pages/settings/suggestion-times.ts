import { Component } from "@angular/core";
import { Location } from "@angular/common";


@Component({
    templateUrl: 'suggestion-times.html'
})
export class SuggestionTimesPage {

    constructor(
        private location:Location
    ){}

    goBack() {
        this.location.back();
    }
}