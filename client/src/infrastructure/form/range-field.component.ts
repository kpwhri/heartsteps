import { Component, forwardRef, Input } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { SelectOption } from "@infrastructure/dialogs/select-dialog.controller";
import { SelectFieldComponent } from "./select-field.component";

@Component({
    selector: 'app-range-field',
    templateUrl: './range-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => RangeFieldComponent)
        }
    ]
})
export class RangeFieldComponent extends SelectFieldComponent {

    public options:Array<SelectOption>;
    public leastLabel:string = 'None';
    public mostLabel:string = 'Most';

    @Input('options')
    set setOptions(options:Array<any>) {
        if(options && options.length >= 2) {
            if(typeof(options[0]) === 'string') {
                this.options = options.map((option, index): SelectOption => {
                    return {
                        name: option,
                        value: index
                    }
                })
            } else {
                this.options = options;
                this.leastLabel = this.options[0].name;
                this.mostLabel = this.options[this.options.length-1].name;
            }
        }
    }

    public updateValue(option: SelectOption) {
        this.writeValue(option);
        this.onChange(option.value);
        this.onTouched();
    }

}
