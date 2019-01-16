import { Component, Output, EventEmitter } from "@angular/core";


@Component({
    templateUrl: './survey.page.html'
})
export class SurveyPageComponent {

    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    constructor() {}

    private done() {
        this.next.emit();
    }

}
