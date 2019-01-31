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
    public errors: Array<string> = [];

    public value: any;

    private statusChangeSubscription: Subscription;

    constructor(
        private formGroup: FormGroupDirective,
        private element: ElementRef,
        private renderer: Renderer2
    ) {}

    ngOnInit() {
        this.renderer.addClass(this.element.nativeElement, 'heartsteps-form-field');
        this.control = this.formGroup.control.get(this.name);
        this.updateDisabled();
        this.statusChangeSubscription = this.control.statusChanges.subscribe(() => {
            this.updateErrors();
            this.updateValidity();
            this.updateDisabled();
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

    public updateErrors(): void {
        this.errors = [];
        if (!this.control.errors) {
            return ;
        }
        if (this.control.errors.required) {
            this.errors.push("This field is required");
        }
    }

    private updateValidity(): void {
        if(!this.control.valid && this.formGroup.touched) {
            this.renderer.addClass(this.element.nativeElement, 'is-invalid');
        } else {
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
        // this.onTouched();
    }

    public isBlurred() {
        this.renderer.removeClass(this.element.nativeElement, 'is-focused');
    }

}
