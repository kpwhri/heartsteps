import { Component, forwardRef, ElementRef, Renderer2, Input } from "@angular/core";
import { NG_VALUE_ACCESSOR, FormGroupDirective } from "@angular/forms";
import { AbstractField } from "./abstract-field";
import { DatePickerDialogController } from "@infrastructure/dialogs/date-picker-dialog.controller";
import { DateFactory } from "@infrastructure/date.factory";


@Component({
    selector: 'app-date-field',
    templateUrl: './date-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => DateFieldComponent)
        }
    ]
})
export class DateFieldComponent extends AbstractField {

    @Input('min-date') minDate:Date;
    @Input('max-date') maxDate:Date;

    constructor(
        formGroup: FormGroupDirective,
        element: ElementRef,
        renderer: Renderer2,
        private dateFactory: DateFactory,
        private datePickerDialog: DatePickerDialogController
    ) {
        super(formGroup, element, renderer);
    }

    public select() {
        const dates = this.dateFactory.getCurrentWeek();
        this.datePickerDialog.choose(dates);
    }
}
