import { Component, ViewChild, OnInit } from "@angular/core";
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from "@angular/forms";
import { Range } from "ionic-angular";


@Component({
    selector: 'heartsteps-range',
    templateUrl: './range.component.html',
    providers: [
        { provide: NG_VALUE_ACCESSOR, useExisting: HeartstepsRangeComponent, multi:true }
    ]
})
export class HeartstepsRangeComponent implements OnInit, ControlValueAccessor  {

    private onChange:Function;
    // tslint:disable-next-line:no-unused-variable
    private onTouched:Function;

    public sliderValue:number = 3;
    public sliderMax: number = 5;
    public sliderMin: number = 1;

    @ViewChild(Range) private range:Range;

    constructor(){}

    ngOnInit() {
        this.range.registerOnChange(() => {
            this.updateValue();
        });
        this.range.max = this.sliderMax;
        this.range.min = this.sliderMin;
        this.writeValue(0.5);
    }

    updateValue() {
        if(this.onChange) {
            this.onChange(this.range.ratio);
        }
    }

    writeValue(ratio:number) {
        const value = (this.sliderMax - this.sliderMin) * ratio;
        this.range.setValue(value + this.sliderMin);
    }

    registerOnChange(fn) {
        this.onChange = fn;
    }

    registerOnTouched(fn) {
        this.onTouched = fn;
    }
}
