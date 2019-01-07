import { Component, forwardRef, OnInit } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { ActivityTypeService, ActivityType } from './activity-type.service';

@Component({
    selector: 'heartsteps-activity-type',
    templateUrl: './activity-type.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => ActivityTypeComponent)
        }
    ]
})
export class ActivityTypeComponent implements ControlValueAccessor, OnInit {
    activityType:ActivityType;
    activityTypeList:Array<ActivityType>;
    onChange;

    constructor(
        private activityTypeService:ActivityTypeService
    ) {}

    ngOnInit() {
        
        this.activityTypeService.load()
        .then((activityTypes) => {
            this.activityTypeList = activityTypes;
        })
    }

    private getActivityType(name:string):Promise<ActivityType> {
        return this.activityTypeService.get()
        .then((activityTypes:Array<ActivityType>) => {
            let activityType:ActivityType;
            activityTypes.forEach((type:ActivityType) => {
                if(name === type.name) {
                    activityType = type;
                }
            })
            if(activityType) {
                return Promise.resolve(activityType);
            } else {
                return Promise.reject("Unknown activity type");
            }
        })
    }

    writeValue(activityName:string): void {
        this.getActivityType(activityName)
        .then((activityType) => {
            this.activityType = activityType;
        })
        .catch(() => {
            this.activityType = null;
        });
    }

    registerOnChange(fn: any): void {
        this.onChange = fn;
    }

    registerOnTouched(fn: any): void {
        
    }

    setDisabledState?(isDisabled: boolean): void {
        
    }

    public select(activityType:ActivityType) {
        this.activityType = activityType;
        this.onChange(activityType.name);
    }

    public reset() {
        this.activityType = null;
        this.onChange(null);
    }
}
