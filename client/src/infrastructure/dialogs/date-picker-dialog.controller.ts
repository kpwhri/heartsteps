import { Injectable } from "@angular/core";

@Injectable()
export class DatePickerDialogController {
    
    constructor() {}

    public choose(options:Array<Date>): Promise<Date> {
        console.log("choose a date");
        console.log(options);
        return Promise.resolve(new Date());
    }

}
