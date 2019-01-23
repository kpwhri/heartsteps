import { Component, forwardRef } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { DateFieldComponent } from "./date-field.component";

@Component({
    selector: 'app-time-field',
    templateUrl: './time-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => TimeFieldComponent)
        }
    ]
})
export class TimeFieldComponent extends DateFieldComponent {

}
