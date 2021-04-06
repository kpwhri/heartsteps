import { Component, Output, EventEmitter, OnInit } from "@angular/core";
import { FormGroup, FormControl } from "@angular/forms";
import { SelectOption } from "@infrastructure/dialogs/select-dialog.controller";
import { MorningMessage } from "@heartsteps/morning-message/morning-message.model";
import { MorningMessageService } from "@heartsteps/morning-message/morning-message.service";
import { LoadingService } from "@infrastructure/loading.service";


@Component({
    templateUrl: './survey.page.html'
})
export class SurveyPageComponent implements OnInit {
    public form: FormGroup;
    public error: string;
    public questions: Array<any>;

    public moodChoices: Array<SelectOption> = [];

    public showWeather: boolean;
    public today: Date;
    
    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    public ready:boolean = false;

    constructor(
        private morningMessageService: MorningMessageService,
        private loadingService: LoadingService
    ) {}

    ngOnInit() {
        this.morningMessageService.get()
        .then((morningMessage) => {
            this.today = morningMessage.date;
        
            if (morningMessage.anchor) {
                this.showWeather = false;
            } else {
                this.showWeather = true;
            }
    
            let response = {}
            if(morningMessage.response) {
                response = morningMessage.response;
            }
    
            this.form = new FormGroup({
                mood: new FormControl(response['selected_word'])
            });
    
            if(morningMessage.survey.wordSet) {
                morningMessage.survey.wordSet.forEach((word:string) => {
                    this.moodChoices.push({
                        name: word,
                        value: word
                    });
                });
            }
    
            if(morningMessage.survey.questions) {
                const questions = [];
                morningMessage.survey.questions.forEach((question) => {
                    questions.push({
                        name: question.name,
                        label: question.label,
                        options: question.options.map((option:any) => {
                            return {
                                name: option.label,
                                value: option.value
                            };
                        })
                    });
                    this.form.addControl(question.name, new FormControl(response[question.name]));
                });
                this.questions = questions;
            }
            this.ready = true;
        });
    }

    public done() {
        this.loadingService.show('Saving survey');
        const values = Object.assign({}, this.form.value);
        values['selected_word'] = values['mood'];
        delete values['mood'];
        this.morningMessageService.submitSurvey(values)
        .then(() => {
            this.next.emit();
        })
        .catch((error) => {
            console.log(error);
            this.error = 'There was an error'
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

}
