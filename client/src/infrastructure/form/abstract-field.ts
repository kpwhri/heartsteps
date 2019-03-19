import { FormGroupDirective, AbstractControl, ControlValueAccessor } from "@angular/forms";
import { ElementRef, Renderer2, OnInit, OnDestroy, Input, Component } from "@angular/core";
import { Subscription } from "rxjs";

@Component({
    template: '<p>Overwrite me</p>'
})
export class AbstractField implements ControlValueAccessor, OnInit, OnDestroy {

    public control: AbstractControl;
    @Input('formControlName') public name: string;

    @Input('label') public label: string;

    public onChange: Function;
    public onTouched: Function;
    public disabled: boolean;
    public isInvalid: boolean;
    public errors: Array<string> = [];
    public error: string;

    public value: any;

    public isFormField: boolean = true;

    private statusChangeSubscription: Subscription;

    constructor(
        public formGroup: FormGroupDirective,
        private element: ElementRef,
        private renderer: Renderer2
    ) {}

    ngOnInit() {
        if (this.isFormField) {
            this.renderer.addClass(this.element.nativeElement, 'heartsteps-form-field');
        }
        this.control = this.formGroup.control.get(this.name);
        this.update();
        this.statusChangeSubscription = this.control.statusChanges.subscribe(() => {
            this.update();
        });
    }

    ngOnDestroy() {
        if(this.statusChangeSubscription) {
            this.statusChangeSubscription.unsubscribe();
        }
    }

    writeValue(value:any): void {
        this.value = value;
    }

    registerOnChange(fn: Function): void {
        this.onChange = fn;
    }

    registerOnTouched(fn: Function): void{
        this.onTouched = fn;
    }

    setDisabledState(isDisabled: boolean): void {
        this.disabled = isDisabled;
    }

    public update(): void {
        this.updateErrors();
        this.updateValidity();
        this.updateDisabled();
    }
 
    public updateErrors(): void {
        this.errors = [];
        this.error = undefined;
        if (!this.control.errors) {
            return ;
        }
        if (this.control.errors.required) {
            this.errors.push("This field is required");
        }
        if(this.errors.length) {
            this.error = this.errors[0];
        }
    }

    private updateValidity(): void {
        if(!this.control.valid && this.control.dirty) {
            this.isInvalid = true;
            this.renderer.addClass(this.element.nativeElement, 'is-invalid');
        } else {
            this.isInvalid = false;
            this.renderer.removeClass(this.element.nativeElement, 'is-invalid');
        }
    }

    private updateDisabled(): void {
        this.disabled = this.control.disabled;
        if(this.control.disabled) {
            this.renderer.addClass(this.element.nativeElement, 'is-disabled');
        } else {
            this.renderer.removeClass(this.element.nativeElement, 'is-disabled');
        }
    }

    public isFocused() {
        this.renderer.addClass(this.element.nativeElement, 'is-focused');
        this.touched();
    }

    public isBlurred() {
        this.renderer.removeClass(this.element.nativeElement, 'is-focused');
    }

    public touched() {
        if(this.onTouched) {
            this.onTouched();
        }
    }

}
