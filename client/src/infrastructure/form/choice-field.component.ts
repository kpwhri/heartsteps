import { Component, forwardRef, Input } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { SelectFieldComponent } from "./select-field.component";
import { SelectOption } from "@infrastructure/dialogs/select-dialog.controller";

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

    public selectedOption:SelectOption;

    public options:Array<SelectOption> = [{
        name: 'Morning',
        value: 'morning'
    }, {
        name: 'Lunch',
        value: 'lunch'
    }, {
        name: 'Mid afternoon',
        value: 'midafternoon'
    }];

    public writeValue(value:string) {
        const option = this.options.find((option) => option.value === value);
        if(option) {
            this.selectedOption = option;
        }
    }

    private setOption(option?:SelectOption) {
        if(option) {
            this.selectedOption = option;
            this.onChange(option.value);
        } else {
            this.selectedOption = undefined;
            this.onChange(undefined);
        }
        this.onTouched();
    }

    public selectOption(option:SelectOption) {
        this.setOption(option);
    }

    public reset() {
        this.setOption();
    }

}
