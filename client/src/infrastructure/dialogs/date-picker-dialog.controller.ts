import { Injectable } from "@angular/core";
import { SelectDialogController, SelectOption } from "./select-dialog.controller";

import * as moment from 'moment';

@Injectable()
export class DatePickerDialogController {
    
    constructor(
        private selectDialog: SelectDialogController
    ) {}

    public choose(options:Array<Date>, selectedValue?:Date): Promise<Date> {
        const selectOptions: Array<SelectOption> = options.map((date) => {
            const option = new SelectOption();
            option.value = date;
            option.name = moment(date).format('dddd, MM/DD')
            return option;
        });
        return this.selectDialog.choose(selectOptions, selectedValue);
    }

}
