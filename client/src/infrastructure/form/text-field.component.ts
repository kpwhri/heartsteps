import { Component, forwardRef } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { AbstractField } from "./abstract-field";

@Component({
    selector: 'app-text-field',
    templateUrl: './text-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => TextFieldComponent)
        }
    ]
})
export class TextFieldComponent extends AbstractField {

}
