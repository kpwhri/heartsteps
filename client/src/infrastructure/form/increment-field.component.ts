import { Component, Input } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { AbstractField } from "./abstract-field";


@Component({
    selector: 'app-increment-field',
    templateUrl: './increment-field.component.html',
    providers: [
        { provide: NG_VALUE_ACCESSOR, useExisting: IncrementFieldComponent, multi:true }
    ]
})
export class IncrementFieldComponent extends AbstractField {

    public value: number;
    public increment: number = 5;

    @Input('units') units:string;

    writeValue(value) {
        if(value) {
            this.value = value;
        } else {
            this.value = value;
        }
    }

    add() {
        this.value += this.increment;
        this.onChange(this.value);
    }

    remove() {
        if(this.value - this.increment <= 0) {
            this.value = 0;
        } else {
            this.value -= this.increment;
        }
        this.onChange(this.value);
    }

}