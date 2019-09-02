import { Component, forwardRef } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { SelectFieldComponent } from "./select-field.component";
import { SelectOption } from "@infrastructure/dialogs/select-dialog.controller";

@Component({
    selector: 'app-select-multiple-field',
    templateUrl: './select-multiple-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => SelectMultipleFieldComponent)
        }
    ]
})
export class SelectMultipleFieldComponent extends SelectFieldComponent {

    public values: Array<any>;
    public selectedOptions: Array<SelectOption>;

    public reset() {
        this.updateValue(undefined);
    }

    public writeValue(value: any) {
        if(Array.isArray(value)) {
            const selectedOptions: Array<SelectOption> = [];
            const values = value.filter((_value) => {
                const option = this.options.find((option) => {
                    return option.value === _value;
                });
                if(option) {
                    selectedOptions.push(option);
                    return option.value;
                }
            });
            this.selectedOptions = selectedOptions;
            this.values = values;
        } else {
            this.values = [];
        }
        this.updateDisplayValue();
    }

    public updateValue(value: any) {
        const _values = [...this.values];
        const valueIndex = _values.indexOf(value);
        if(valueIndex >= 0) {
            _values.splice(valueIndex, 1);
        } else {
            _values.push(value);
        }
        this.writeValue(_values);
        this.onChange(_values);
        this.onTouched();
    }

    public isSelected(value: any): boolean {
        if(this.values.indexOf(value) >= 0) {
            return true;
        } else {
            return false;
        }
    }

}
