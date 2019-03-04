import { Component, Output, EventEmitter, Input } from '@angular/core';

import { LoadingService } from '@infrastructure/loading.service';
import { Week } from './week.model';
import { FormGroup, FormControl, Validators } from '@angular/forms';

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

    public form: FormGroup;

    constructor(
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
        this.loadingService.show("Saving goal");
        this._week.setGoal(this.form.value.minutes, this.form.value.confidence)
        .then(() => {
            this.loadingService.dismiss();
            this.saved.emit();
        })
    }
    

}
