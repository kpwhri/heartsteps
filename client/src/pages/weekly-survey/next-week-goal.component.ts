import { Component, OnInit, Output, EventEmitter } from "@angular/core";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { WeeklySurveyService } from "@heartsteps/weekly-survey/weekly-survey.service";
import { LoadingService } from "@infrastructure/loading.service";

@Component({
    templateUrl: './next-week-goal.component.html'
})
export class NextWeekGoalComponent implements OnInit {

    public nextWeek:Week;
    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    constructor(
        private weeklySurveyService: WeeklySurveyService,
        private loadingService: LoadingService
    ) {}

    ngOnInit() {
        this.loadingService.show('Loading next week');
        this.weeklySurveyService.get()
        .then((weeklySurvey) => {
            this.nextWeek = weeklySurvey.nextWeek;
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    nextPage() {
        this.next.emit();
    }

}
