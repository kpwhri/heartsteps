import { Component, forwardRef, OnInit, Input } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { ActivityTypeService, ActivityType } from './activity-type.service';
import { ActivityTypeModalController } from './activity-type-modal.controller';

@Component({
    selector: 'heartsteps-activity-type-field',
    templateUrl: './activity-type-field.component.html',
    providers: [
        ActivityTypeModalController,
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => ActivityTypeFieldComponent)
        }
    ]
})
export class ActivityTypeFieldComponent implements ControlValueAccessor, OnInit {
    public activityType:ActivityType;
    public activityTypeList:Array<ActivityType>;
    
    private onChange: Function;
    private onTouched: Function;
    public isDisabled: boolean;

    @Input('label') label: string = 'Activity type';

    constructor(
        private activityTypeService:ActivityTypeService,
        private activityTypeModalController: ActivityTypeModalController
    ) {}

    ngOnInit() {
        this.activityTypeService.activityTypes.subscribe((activityTypes) => {
            if(activityTypes) {
                this.activityTypeList = activityTypes.slice(0, 4);
            } else {
                this.activityTypeList = [];
            }
        });
    }

    private getActivityType(name:string):Promise<ActivityType> {
        return this.activityTypeService.get(name);
    }

    writeValue(activityName:string): void {
        this.getActivityType(activityName)
        .then((activityType) => {
            this.activityType = activityType;
        })
        .catch(() => {
            this.activityType = undefined;
        });
    }

    registerOnChange(fn: any): void {
        this.onChange = fn;
    }

    registerOnTouched(fn: any): void {
        this.onTouched = fn;
    }

    setDisabledState?(isDisabled: boolean): void {
        this.isDisabled = isDisabled;
    }

    public select(activityType:ActivityType) {
        if(!this.isDisabled) {
            this.activityType = activityType;
            this.onChange(activityType.name);
            this.onTouched();
        }
    }

    public reset() {
        if (!this.isDisabled) {
            this.activityType = undefined;
            this.onChange(undefined);
        }
    }

    public pickOtherActivityType() {
        this.activityTypeModalController.pick()
        .then((activityType) => {
            this.select(activityType);
        })
        .catch(() => {
            console.log('Dismissed');
        })
    }
}
