import { Component, Input, Output, EventEmitter } from "@angular/core";
import { FormGroup } from "@angular/forms";


@Component({
    selector: 'app-form',
    templateUrl: './form.component.html'
})
export class FormComponent {

    @Output('onSubmit') public onSubmit: EventEmitter<boolean> = new EventEmitter();

    public form: FormGroup;

    private errorMessage: string;
    public submitCTA: string;

    constructor() {}

    @Input('submitLabel')
    set submitLabel(text: string) {
        if(text) {
            this.submitCTA = text;
        } else {
            this.submitCTA = 'Save';
        }
    }

    @Input('formGroup')
    set setForm(form: FormGroup) {
        if (form) {
            this.form = form;
        }
    }

    @Input('error')
    set setErrorMessage(error: string) {
        if (error || (error === undefined && this.errorMessage)) {
            this.errorMessage = error;
        }
    }
    
    public formSubmit() {
        this.submit()
        .then(() => {
            this.onSubmit.emit();
        });
    }

    public submit(): Promise<boolean> {
        this.errorMessage = undefined;
        if(this.form.valid) {
            return Promise.resolve(true);
        } else {
            this.errorMessage = 'Invalid form';
            return Promise.reject('Invalid form');
        }
    }
}
