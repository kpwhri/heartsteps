import { Component, forwardRef, Input } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";

import * as moment from 'moment';
import { SelectFieldComponent } from "./select-field.component";
import { SelectOption } from "@infrastructure/dialogs/select-dialog.controller";

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
export class DateFieldComponent extends SelectFieldComponent {

    // tslint:disable-next-line:no-unused-variable
    private date: Date;

    private formatDate(date:Date):string {
        return moment(date).format('dddd, MM/DD');
    }

    public writeValue(date:Date) {
        this.date = date;
        this.value = this.formatDate(date);
    }

    public updateValue(value:string) {
        console.log(value);
        const date:Date = moment(value, 'dddd, MM/DD').toDate();
        console.log(date);
        this.writeValue(date);
        this.onChange(date);
    }

    @Input('available-dates')
    set setAvailableDates(dates: Array<Date>) {
        this.options = dates.map((date: Date) => {
            const option = new SelectOption();
            option.name = this.formatDate(date);
            option.value = this.formatDate(date);
            return option;
        })
    }
}
