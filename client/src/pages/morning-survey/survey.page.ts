import { Component, Output, EventEmitter } from "@angular/core";
import { FormGroup, FormControl } from "@angular/forms";
import { SelectOption } from "@infrastructure/dialogs/select-dialog.controller";


@Component({
    templateUrl: './survey.page.html'
})
export class SurveyPageComponent {
    public form: FormGroup;
    public moodChoices: Array<SelectOption>;
    public busyOptions: Array<string>;
    public restedOptions: Array<string>;
    public committedOptions: Array<string>;
    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    constructor() {
        this.form = new FormGroup({
            busy: new FormControl(),
            rested: new FormControl(),
            committed: new FormControl(),
            mood: new FormControl()
        });

        this.busyOptions = ['Not at all busy', 'A little busy', 'Moderately busy', 'Pretty busy', 'Very busy'];
        this.restedOptions = ['Not at all rested', 'A little rested', 'Moderately rested', 'Quite rested', 'Very rested'];
        this.committedOptions = ['Not at all committed', 'A little committed', 'Moderately committed', 'Quite committed', 'Very committed'];

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
