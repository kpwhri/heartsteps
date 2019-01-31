import { Component, forwardRef } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { SelectFieldComponent } from "./select-field.component";
import { SelectOption } from "@infrastructure/dialogs/select-dialog.controller";

import * as moment from 'moment';

@Component({
    selector: 'app-time-field',
    templateUrl: './time-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => TimeFieldComponent)
        }
    ]
})
export class TimeFieldComponent extends SelectFieldComponent {

    private date: Date;

    public formatTime(date:Date): String {
        return moment(date).format('h:mm A')
    }

    public writeValue(date:Date) {
        this.date = date;
        this.value = this.formatTime(date);
    }

    public showDialog() {
        this.selectDialog.chooseMultiple([{
            name: 'hour',
            selectedValue: this.getHours(),
            options: this.getHourOptions(),
            width: '40px'
        }, {
            name: 'minute',
            selectedValue: this.getMinutes(),
            options: this.getMinuteOptions(),
            width: '40px'
        }, {
            name: 'ampm',
            selectedValue: this.getAMPM(),
            options: this.getAMPMOptions(),
            width: '40px'
        }])
        .then((data) => {
            let hours = data.hour.value;
            if (data.ampm.value) {
                hours += 12;
            }
            this.date.setHours(hours);
            this.date.setMinutes(data.minute.value);
            this.writeValue(this.date);
            this.onChange(this.date);
        })
        .catch(() => {
            console.log("nothing selected.")
        })
    }

    private getHours(): number {
        let hours = this.date.getHours();
        if(hours > 12) {
            return hours - 12;
        } else {
            return hours;
        }
    }

    private getMinutes(): number {
        return this.date.getMinutes();
    }

    private getAMPM(): boolean {
        if(this.date.getHours() >= 12) {
            return true;
        } else {
            return false;
        }
    }

    private getHourOptions(): Array<SelectOption> {
        const hours: Array<SelectOption> = [];
        let i:number = 1;
        while(i <= 12) {
            hours.push({
                name: this.formatNumber(i),
                value: i
            })
            i++;
        }
        return hours;
    }

    private getMinuteOptions(): Array<SelectOption> {
        const minutes: Array<Number> = [];
        let i:number = 0;
        while(i < 60) {
            minutes.push(i);
            i = i + 5;
        }
        const selectedMinute:Number = this.getMinutes();
        if (minutes.indexOf(selectedMinute) < 0) {
            minutes.push(selectedMinute);
            minutes.sort();
        }
        return minutes.map((minute) => {
            return {
                name: this.formatNumber(minute),
                value: minute
            }
        })
    }

    private getAMPMOptions(): Array<SelectOption> {
        return [{
            name: 'am',
            value: false
        }, {
            name: 'pm',
            value: true
        }];
    }

    private formatNumber(num: Number): string {
        if(num < 10) {
            return '0' + String(num);
        } else {
            return String(num);
        }
    }

}
