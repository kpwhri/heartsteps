import { Component } from "@angular/core";
import { Location } from "@angular/common";


@Component({
    templateUrl: 'reflection-time-page.html'
})
export class ReflectionTimePage {

    constructor(
        private location:Location
    ){}

    goBack() {
        this.location.back();
    }
}
