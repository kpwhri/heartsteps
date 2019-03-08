import { Component, forwardRef, Input } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { SelectFieldComponent } from "./select-field.component";

@Component({
    selector: 'app-choice-field',
    templateUrl: './choice-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => ChoiceFieldComponent)
        }
    ]
})
export class ChoiceFieldComponent extends SelectFieldComponent {

    public reset() {
        this.updateValue(undefined);
    }

}
