import { Component, Output, EventEmitter } from "@angular/core";

@Component({
    templateUrl: './survey.component.html'
})
export class SurveyComponent {

    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    constructor() {}

    nextPage() {
        this.next.emit();
    }

}
