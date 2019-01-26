import { Component, forwardRef, Input, ElementRef, Renderer2 } from "@angular/core";
import { NG_VALUE_ACCESSOR, FormGroupDirective } from "@angular/forms";
import { AbstractField } from "./abstract-field";
import { SelectOption, SelectDialogController } from "@infrastructure/dialogs/select-dialog.controller";

@Component({
    selector: 'app-select-field',
    templateUrl: './select-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => SelectFieldComponent)
        }
    ]
})
export class SelectFieldComponent extends AbstractField {

    @Input('options') public options:Array<SelectOption>

    constructor(
        formGroup: FormGroupDirective,
        element: ElementRef,
        renderer: Renderer2,
        public selectDialog: SelectDialogController
    ) {
        super(formGroup, element, renderer);
    }

    public select() {
        this.onTouched();
        this.showDialog();
    }

    public showDialog() {
        this.selectDialog.choose(this.options, this.value)
        .then((value) => {
            this.updateValue(value);
        })
        .catch(() => {
            console.log('Nothing selected');
        });
    }

    public updateValue(value:any) {
        this.writeValue(value);
        this.onChange(value);
    }

}
