import { Component, Output, EventEmitter, OnInit } from "@angular/core";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { WeeklySurveyService } from "@heartsteps/weekly-survey/weekly-survey.service";
import { LoadingService } from "@infrastructure/loading.service";

@Component({
    templateUrl: './next-week-plans.component.html'
})
export class NextWeekPlansComponent implements OnInit {

    @Output('next') next:EventEmitter<boolean> = new EventEmitter();
    public nextWeek: Week;

    constructor(
        private weeklySurveyService: WeeklySurveyService,
        private loadingService: LoadingService
    ) {}

    ngOnInit() {
        this.loadingService.show('Loading plans');
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
