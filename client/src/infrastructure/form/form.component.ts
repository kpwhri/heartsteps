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
    private submitCTA: string = 'Save';

    @Input('defaultSubmit') showSubmit: boolean = true;

    constructor() {}

    @Input('formGroup')
    set setForm(form: FormGroup) {
        if (form) {
            this.form = form;
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
