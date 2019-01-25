import { Component, Input, Output, EventEmitter } from "@angular/core";
import { FormGroup } from "@angular/forms";


@Component({
    selector: 'app-form',
    templateUrl: './form.component.html'
})
export class FormComponent {

    @Output('onSubmit') public onSubmit: EventEmitter<boolean> = new EventEmitter();

    public formGroup: FormGroup;

    private errorMessage: string;
    private submitCTA: string = 'Save';

    constructor() {}

    @Input('form')
    set setForm(form: FormGroup) {
        if (form) {
            this.formGroup = form;
        }
    }

    public submit(): Promise<boolean> {
        this.errorMessage = undefined;
        if(this.formGroup.valid) {
            this.onSubmit.emit();
            return Promise.resolve(true);
        } else {
            this.errorMessage = 'Invalid form';
            return Promise.reject('Invalid form');
        }
    }
}
