import { Component, forwardRef } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { AbstractField } from "./abstract-field";

@Component({
    selector: 'app-year-field',
    templateUrl: './year-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => YearFieldComponent)
        }
    ]
})
export class YearFieldComponent extends AbstractField {

}
