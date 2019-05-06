import { Component, forwardRef } from "@angular/core";
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from "@angular/forms";

@Component({
    selector: 'activity-enjoyed-field',
    templateUrl: './activity-enjoyed-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => ActivityEnjoyedFieldComponent)
        }
    ]
})
export class ActivityEnjoyedFieldComponent implements ControlValueAccessor {

    public selectedIndex: number;
    public options = [
        'Not enjoyed',
        'Little enjoyment',
        'Some enjoyment',
        'Fully enjoyed'
    ];

    private onChange: Function;
    private onTouched: Function;
    public isDisabled: boolean;

    constructor() {}

    public select(index:number) {
        this.selectedIndex = index;
        if(this.options.length > 1) {
            const value:number = index/(this.options.length-1);
            this.onChange(value);
            this.onTouched();
        }
    }

    public writeValue(enjoyed: number) {
        if(enjoyed === null) {
            this.selectedIndex = null;
        } else {
            const value = Math.round((this.options.length-1) * enjoyed);
            console.log('write value ' + value);
            this.selectedIndex = value;
        }
    }

    public registerOnChange(fn: Function) {
        this.onChange = fn;
    }

    public registerOnTouched(fn: Function) {
        this.onTouched = fn;
    }

    public setDisabledState(isDisabled: boolean) {
        this.isDisabled = isDisabled;
    }

}
