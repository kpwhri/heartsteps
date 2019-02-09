import { Component, Output, EventEmitter } from "@angular/core";


@Component({
    selector: 'page-weekly-survey-start',
    templateUrl: './survey-start.html'
})
export class SurveyStartPage {

    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    constructor() {}

    nextPage() {
        this.next.emit();
    }
}