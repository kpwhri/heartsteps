import { Component, Input } from "@angular/core";
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from "@angular/forms";


@Component({
    selector: 'heartsteps-increment',
    templateUrl: './increment.component.html',
    inputs: ['title', 'units'],
    providers: [
        { provide: NG_VALUE_ACCESSOR, useExisting: HeartstepsIncrementComponent, multi:true }
    ]
})
export class HeartstepsIncrementComponent implements ControlValueAccessor {

    private onChange: Function;
    private onTouch: Function;

    private amount: number;
    private increment: number = 5;

    @Input() title:string;
    @Input() units:string;

    constructor(){}

    writeValue(value) {
        if(value) {
            this.amount = value;
        } else {
            this.amount = value;
        }
    }

    add() {
        this.amount += this.increment;
        this.onChange(this.amount);
    }

    remove() {
        if(this.amount - this.increment <= 0) {
            this.amount = 0;
        } else {
            this.amount -= this.increment;
        }
        this.onChange(this.amount);
    }

    registerOnChange(fn) {
        this.onChange = fn;
    }

    registerOnTouched(fn) {
        this.onTouch = fn;
    }

}