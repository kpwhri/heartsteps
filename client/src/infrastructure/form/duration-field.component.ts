import { Component, forwardRef, Input } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { AbstractField } from "./abstract-field";


@Component({
    selector: 'app-duration-field',
    templateUrl: './duration-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => DurationFieldComponent)
        }
    ]
})
export class DurationFieldComponent extends AbstractField  {

    @Input('unit-label') public unitLabel: string = "min";

    public duration: Number;

    updateDuration(duration: Number): void {
        this.onChange(duration);
        this.onTouched();
    }

    writeValue(duration: Number) {
        this.duration = duration;
    }

}
