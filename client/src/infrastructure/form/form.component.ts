import { Component, Input, Output, EventEmitter, OnDestroy } from "@angular/core";
import { FormGroup } from "@angular/forms";
import { Subscription } from "rxjs";


@Component({
    selector: 'app-form',
    templateUrl: './form.component.html'
})
export class FormComponent implements OnDestroy {

    @Output('onSubmit') public onSubmit: EventEmitter<boolean> = new EventEmitter();

    public form: FormGroup;
    public disabled: boolean = false;

    private errorMessage: string;
    public submitCTA: string = 'Save';

    private formStatusSubscription: Subscription;

    constructor() {}

    ngOnDestroy() {
        if(this.formStatusSubscription) {
            this.formStatusSubscription.unsubscribe();
        }
    }

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
            this.formStatusSubscription = this.form.statusChanges.subscribe(() => {
                if(this.form.valid) {
                    this.errorMessage = undefined;
                }
            });
        }
    }

    @Input('error')
    set setErrorMessage(error: string) {
        if (error || (error === undefined && this.errorMessage)) {
            this.errorMessage = error;
        }
    }

    @Input('disabled')
    set setDisabled(disabled:boolean) {
        if(disabled !== undefined) {
            this.disabled = disabled;
            if(this.form && disabled) {
                this.form.disable();
            }
            if(this.form && !disabled) {
                this.form.enable();
            }
            
        }
    }
    
    public formSubmit() {
        this.submit()
        .then(() => {
            this.onSubmit.emit();
        })
        .catch((error) => {
            console.log(error);
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
