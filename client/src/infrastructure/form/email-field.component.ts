import { Component, forwardRef } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { AbstractField } from "./abstract-field";

@Component({
    selector: 'app-email-field',
    templateUrl: './email-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => EmailFieldComponent)
        }
    ]
})
export class EmailFieldComponent extends AbstractField {

}
