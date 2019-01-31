import { Component, OnInit, forwardRef, Input } from "@angular/core";
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from "@angular/forms";



@Component({
    selector: 'heartsteps-activity-intensity-field',
    templateUrl: './activity-intensity-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => ActivityIntensityFieldComponent)
        }
    ]
})
export class ActivityIntensityFieldComponent implements ControlValueAccessor {

    public isVigorous: boolean;

    private onChange: Function;
    private onTouched: Function;
    public isDisabled: boolean;

    @Input('label') label: string = 'Intensity';

    constructor() {}

    public update(vigorous:boolean) {
        this.isVigorous = vigorous;
        this.onTouched();
        this.onChange(vigorous);
    }

    writeValue(vigorous:boolean) {
        this.isVigorous = vigorous;
    }

    registerOnChange(fn: Function) {
        this.onChange = fn;
    }

    registerOnTouched(fn: Function) {
        this.onTouched = fn;
    }

    setDisabledState(isDisabled: boolean) {
        this.isDisabled = isDisabled;
    }
}
