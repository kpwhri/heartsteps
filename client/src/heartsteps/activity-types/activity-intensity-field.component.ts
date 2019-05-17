import { Component, forwardRef, Input } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { AbstractField } from "@infrastructure/form/abstract-field";



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
export class ActivityIntensityFieldComponent extends AbstractField {

    public isVigorous: boolean;

    @Input('label') label: string = 'Intensity';

    public updateVigorous(vigorous:boolean) {
        this.isVigorous = vigorous;
        this.onTouched();
        this.onChange(vigorous);
    }

    writeValue(vigorous:boolean) {
        this.isVigorous = vigorous;
    }
}
