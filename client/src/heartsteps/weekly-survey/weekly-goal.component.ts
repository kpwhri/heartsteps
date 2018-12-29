import { Component, Output, EventEmitter, Input } from '@angular/core';

import { loadingService } from '@infrastructure/loading.service';
import { Week } from './week.model';
import { WeekService } from './week.service';

@Component({
  selector: 'heartsteps-weekly-goal',
  templateUrl: './weekly-goal.component.html',
  inputs: ['week']
})
export class WeeklyGoalComponent {

    @Output() saved = new EventEmitter<boolean>();

    public minutes:number;
    public confidence:number;
    private _week:Week;

    constructor(
        private loadingService:loadingService,
        private weekService:WeekService
    ) {}

    @Input()
    set week(week:Week) {
        if(week) {
            this._week = week;
            this.minutes = week.goal;
            this.confidence = week.confidence;
        }
    }

    addFiveMinutes() {
        this.minutes += 5;
    }

    removeFiveMinutes() {
        if(this.minutes - 5 <= 0) {
            this.minutes = 0;
        } else {
            this.minutes -= 5;
        }
    }

    save() {
        this._week.goal = this.minutes;
        this._week.confidence = this.confidence;
        this.loadingService.show("Saving goal");
        this.weekService.setWeekGoal(this._week)
        .then(() => {
            this.loadingService.dismiss();
            this.saved.emit();
        });
    }
    

}
