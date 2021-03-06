import { Component, Output, EventEmitter, Input } from '@angular/core';

import { LoadingService } from '@infrastructure/loading.service';
import { Week } from './week.model';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { WeekService } from './week.service';
import { SelectOption } from '@infrastructure/dialogs/select-dialog.controller';

@Component({
  selector: 'heartsteps-weekly-goal',
  templateUrl: './weekly-goal.component.html'
})
export class WeeklyGoalComponent {

    @Input('call-to-action') cta:string = "Set goal";
    @Output() saved = new EventEmitter<boolean>();

    public minutes:number;
    public confidence:number;
    private _week:Week;

    public confidenceOptions: Array<SelectOption> = [
        {
            name: 'Not at all',
            value: 0
        }, {
            name: 'Some confidence',
            value: 0.25
        }, {
            name: 'Moderate confidence',
            value: 0.5
        }, {
            name: 'Fairly confident',
            value: 0.75
        }, {
            name: 'Very much',
            value: 1
        }
    ]

    public form: FormGroup;
    public error: string;

    constructor(
        private weekService: WeekService,
        private loadingService:LoadingService
    ) {}

    @Input()
    set week(week:Week) {
        if(week) {
            this._week = week;
            this.form = new FormGroup({
                minutes: new FormControl(week.goal, Validators.required),
                confidence: new FormControl(week.confidence)
            });
        }
    }

    save() {
        this.error = undefined;
        this.loadingService.show("Saving goal");
        this.weekService.setWeekGoal(this._week, this.form.value.minutes, this.form.value.confidence)
        .then(() => {
            this.saved.emit();
        })
        .catch((error) => {
            this.error = error;
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }
    

}
