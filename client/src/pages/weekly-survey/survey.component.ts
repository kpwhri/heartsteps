import { Component, Output, EventEmitter } from "@angular/core";
import { FormGroup, FormControl } from "@angular/forms";

@Component({
    templateUrl: './survey.component.html'
})
export class SurveyComponent {

    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    public form: FormGroup;

    public trueOptions: Array<string> = [
        'Not at all true',
        'A little true',
        'Moderately true',
        'Mostly true',
        'Very true'
    ]

    public muchOptions: Array<string> = [
        'Not at all',
        'A little',
        'Some',
        'Mostly',
        'Very much'
    ]

    constructor() {

        this.form = new FormGroup({
            enjoy: new FormControl(),
            fit: new FormControl(),
            supported: new FormControl(),
            important: new FormControl(),
            other: new FormControl(),
            stressed: new FormControl()
        });
    }

    nextPage() {
        this.next.emit();
    }

}
