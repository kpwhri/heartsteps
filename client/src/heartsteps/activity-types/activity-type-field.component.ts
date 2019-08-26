import { Component, forwardRef, Input, ElementRef, Renderer2 } from '@angular/core';
import { NG_VALUE_ACCESSOR, FormGroupDirective } from '@angular/forms';
import { ActivityTypeService, ActivityType } from './activity-type.service';
import { ActivityTypeModalController } from './activity-type-modal.controller';
import { ChoiceFieldComponent } from '@infrastructure/form/choice-field.component';
import { SelectDialogController, SelectOption } from '@infrastructure/dialogs/select-dialog.controller';

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
export class ActivityTypeFieldComponent extends ChoiceFieldComponent {
    public activityType:ActivityType;
    private activityTypes: Array<ActivityType>;

    @Input('label') label: string = 'Activity type';

    constructor(
        formGroup: FormGroupDirective,
        element: ElementRef,
        renderer: Renderer2,
        public selectDialog: SelectDialogController,
        private activityTypeService:ActivityTypeService,
        private activityTypeModalController: ActivityTypeModalController
    ) {
        super(formGroup, element, renderer, selectDialog);
        this.activityTypeService.activityTypes
        .filter((activityTypes) => activityTypes !== undefined)
        .subscribe((activityTypes) => {
            this.activityTypes = activityTypes;
            this.updateOptions();
        });
    }

    private getActivityType(name:string):Promise<ActivityType> {
        return this.activityTypeService.get(name);
    }

    writeValue(activityName:string): void {
        this.selectedOption = undefined;
        this.updateOptions();
        this.getActivityType(activityName)
        .then((activityType) => {
            this.activityType = activityType;
            this.selectedOption = {
                name: activityType.title,
                value: activityType.name
            }
        })
        .catch(() => {
            this.activityType = undefined;
            this.selectedOption = undefined;
        });
    }

    public updateOptions() {
        const options:Array<SelectOption> = [];
        this.activityTypes.slice(0,4).forEach((activityType) => {
            options.push({
                name: activityType.title,
                value: activityType.name
            });
        });
        this.options = options;
    }

    public pickOtherActivityType() {
        this.activityTypeModalController.pick()
        .then((activityType) => {
            this.updateValue(activityType.name);
        })
        .catch(() => {
            console.log('Dismissed');
        });
    }
}
