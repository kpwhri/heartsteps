import { Component, forwardRef, Input, ElementRef, Renderer2 } from "@angular/core";
import { NG_VALUE_ACCESSOR, FormGroupDirective } from "@angular/forms";
import { AbstractField } from "./abstract-field";
import { SelectOption, SelectDialogController } from "@infrastructure/dialogs/select-dialog.controller";

@Component({
    selector: 'app-select-field',
    templateUrl: './select-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => SelectFieldComponent)
        }
    ]
})
export class SelectFieldComponent extends AbstractField {

    @Input('options') public options:Array<SelectOption>
    public selectedOption: SelectOption;
    public displayValue: string;

    constructor(
        formGroup: FormGroupDirective,
        element: ElementRef,
        renderer: Renderer2,
        public selectDialog: SelectDialogController
    ) {
        super(formGroup, element, renderer);
    }

    public select() {
        this.onTouched();
        this.showDialog();
    }

    public showDialog() {
        this.selectDialog.choose(this.options, this.value)
        .then((value) => {
            this.updateValue(value);
        })
        .catch(() => {
            console.log('Nothing selected');
        });
    }

    public writeValue(value:any) {
        this.value = value;
        this.selectedOption = undefined;
        if(this.options && this.options.length) {
            const option = this.options.find((option) => {
                return option.value === value
            });
            if(option) {
                this.selectedOption = option;
                this.value = option.value;
            }
        }
        this.updateDisplayValue();
    }

    public updateDisplayValue() {
        let option: SelectOption;
        if (this.options && this.options.length) {
            option = this.options.find((option) => {
                return option.value === this.value;
            });
        }
        if(option) {
            this.displayValue = option.name;
        } else {
            this.displayValue = undefined;
        }
    }

    public updateValue(value:any) {
        this.writeValue(value);
        this.onChange(value);
        this.onTouched();
    }

}
