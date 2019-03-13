import { Component, Output, EventEmitter } from "@angular/core";
import { FormGroup, FormControl } from "@angular/forms";
import { SelectOption } from "@infrastructure/dialogs/select-dialog.controller";


@Component({
    templateUrl: './survey.page.html'
})
export class SurveyPageComponent {
    public form: FormGroup;
    public moodChoices: Array<SelectOption>;
    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    constructor() {
        this.form = new FormGroup({
            busy: new FormControl(),
            rested: new FormControl(),
            committed: new FormControl(),
            mood: new FormControl()
        })

        this.moodChoices = [{
            name: 'Alert',
            value: 'alert'
        }, {
            name: 'Fatigued',
            value: 'fatigued'
        }, {
            name: 'Tense',
            value: 'tense'
        }, {
            name: 'Calm',
            value: 'calm'
        }];
    }

    public done() {
        this.next.emit();
    }

}
