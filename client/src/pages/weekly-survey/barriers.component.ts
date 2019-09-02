import { Component, Output, EventEmitter, OnInit } from "@angular/core";
import { FormGroup, FormControl } from "@angular/forms";
import { ActivatedRoute } from "@angular/router";
import { WeeklySurvey } from "@heartsteps/weekly-survey/weekly-survey.service";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { LoadingService } from "@infrastructure/loading.service";
import { WeeklySurveyService } from "@heartsteps/weekly-survey/weekly-survey.service";
import { SelectOption } from "@infrastructure/dialogs/select-dialog.controller";
import { BarrierModalController } from "./barrier-modal.controller";

@Component({
    templateUrl: './barriers.component.html',
    providers: [
        BarrierModalController
    ]
})
export class BarriersComponent implements OnInit {

    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    public form: FormGroup;

    public week: Week;
    private weeklySurvey: WeeklySurvey;

    public barriers: Array<string>;
    public barrierOptions: Array<SelectOption>;
    public willCompleteOptions: Array<SelectOption>;

    constructor(
        private activatedRoute: ActivatedRoute,
        private barrierModalController: BarrierModalController,
        private weeklySurveyService: WeeklySurveyService,
        private loadingService: LoadingService
    ) {}

    ngOnInit() {
        this.form = new FormGroup({});

        this.weeklySurvey = this.activatedRoute.snapshot.data['weeklySurvey'];
        this.week = this.weeklySurvey.currentWeek;
        this.barriers = this.weeklySurvey.barriers;

        this.form.addControl('barriers', new FormControl([...this.barriers]));
        this.form.addControl('willBarriersContinue', new FormControl(this.weeklySurvey.willBarriersContinue));

        this.barrierOptions = this.weeklySurvey.barrierOptions.map((option) => {
            const selectOption = new SelectOption();
            selectOption.name = option;
            selectOption.value = option;
            return selectOption;
        });
        this.updateOptions();
        this.willCompleteOptions = [
            {
                name: 'Yes',
                value: 'yes'
            },
            {
                name: 'No',
                value: 'no'
            },
            {
                name: 'I am not sure',
                value: 'unknown'
            }
        ]

    }

    public nextPage() {
        this.loadingService.show('Saving barriers');
        const barriers = this.form.get('barriers').value;
        const willContinue = this.form.get('willBarriersContinue').value;
        this.weeklySurveyService.submitBarriers(barriers, willContinue)
        .then(() => {
            this.next.emit();
        })
        .catch((error) => {
            console.log(error);
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public addBarrier() {
        this.barrierModalController.newBarrier()
        .then((barrier) => {
            this.barriers = this.form.get('barriers').value;
            const barrierIndex = this.barriers.indexOf(barrier);
            if(barrierIndex === -1) {
                this.barriers.push(barrier);
            }
            this.updateOptions()

            setTimeout(() => {
                this.form.patchValue({
                    barriers: [...this.barriers]
                });
            });
        })
        .catch(() => {
            return;
        });
    }

    private updateOptions() {

        const customBarriers = this.barriers.filter((barrier) => {
            const barrierOption = this.barrierOptions.find((option) => {
                return option.value === barrier;
            });
            return barrierOption === undefined;
        });
        customBarriers.forEach((barrier) => {
            this.barrierOptions.push({
                name: barrier,
                value: barrier
            });
        });
    }

}
