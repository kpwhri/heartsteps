import { Component, forwardRef } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { AbstractField } from "./abstract-field";

@Component({
    selector: 'app-phone-field',
    templateUrl: './phone-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => PhoneFieldComponent)
        }
    ]
})
export class PhoneFieldComponent extends AbstractField {

}
