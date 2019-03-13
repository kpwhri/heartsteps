import { Component, forwardRef, Input } from "@angular/core";
import { NG_VALUE_ACCESSOR } from "@angular/forms";
import { AbstractField } from "./abstract-field";

@Component({
    selector: 'app-range-field',
    templateUrl: './range-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => RangeFieldComponent)
        }
    ]
})
export class RangeFieldComponent extends AbstractField {

    public selectedIndex: number;
    public options:Array<string> = [
        'None',
        'Some',
        'Moderate',
        'Lots',
        'Maximum'
    ];
    public leastLabel:string = 'None';
    public mostLabel:string = 'Most';

    @Input('options')
    set setOptions(options:Array<string>) {
        if(options && options.length >= 2) {
            this.options = options;
            this.leastLabel = this.options[0];
            this.mostLabel = this.options[this.options.length-1];
        }
    }

    public select(index:number) {
        this.selectedIndex = index;
        if(this.options.length > 1) {
            const value:number = index/(this.options.length-1);
            this.onChange(value);
            this.onTouched();
        }
    }

    public writeValue(value:any) {
        if(value === null) {
            this.selectedIndex = null;
        } else {
            const newValue = Math.round((this.options.length-1) * value);
            console.log('write value ' + value);
            this.selectedIndex = newValue;
        }
    }

    public updateValue(value:any) {
        this.onChange(value);
    }

}
